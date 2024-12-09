import random
import itertools
import numpy as np
import pandas as pd
import streamlit as st


from collections import Counter, defaultdict

from backend.candidateSystemGenerator.Marginalization import Marginalization

from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from backend.marginalizacion import obtener_tabla_probabilidades

class SecondStrategy:
    
    def __init__(self, probabilities, cs_value, states, cs, ns, futureTables, st2_candidateSystem, varData):
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.memory = {}
        self.states = states
        self.min_emd = float("inf")
        self.mejor_particion = []
        self.cs = cs
        self.ns = ns
        self.candidateSystem = st2_candidateSystem
        self.futureTables = futureTables
        self.marginalization = Marginalization(probabilities,st2_candidateSystem, varData)

        st.write("Estado Original")
        st.text(f"{self.cs_value}")

        st2_candidateSystem_Imperfect = self.marginalization.indexCandidateSystem()
        st2_candidateSystem_Perfect = self.marginalization.marginalize_variableFuture(st2_candidateSystem_Imperfect)

        st.subheader("Tabla de Sistema Candidato - Imperfecta")
        #st.table(st2_candidateSystem_Imperfect)

        st.subheader("Tabla de Sistema Candidato - Perfecta (Marginalizada)")
        #st.table(st2_candidateSystem_Perfect)

        self.original_system = st2_candidateSystem_Perfect[(int(self.cs_value, 2))]

        st.write("Validación Estado Original")
        st.text(f"{self.original_system}")    

        st.divider()    

    def Cortar(self, Lista):
        Corte = Lista[-2:]
        Corte_unido = []
        for elem in Corte:
            if isinstance(elem, list):
                Corte_unido.extend(elem)
            else:
                Corte_unido.append(elem)

        Arreglo = Lista[:-2]
        Arreglo.append(Corte_unido)
        return Arreglo
    
    def descomponer(self, ns, cs):
        if self.memory.get(cs) is not None and self.memory.get(cs).get(ns) is not None:
            if any(self.memory.get(cs).get(ns)):
                return self.memory.get(cs).get(ns)

        if len(ns) == 1:
            value = obtener_tabla_probabilidades(
                repr_current_to_array(cs, self.cs_value),
                repr_next_to_array(ns),
                self.probabilities,
                self.states,
            )
            return value

        value = []
        for i in range(0, len(ns)):
            if len(value) > 0:
                cross_product = np.kron(value, self.descomponer(ns[i], cs))
                value = ordenar_matriz_product(cross_product)
            else:
                value = np.array(self.descomponer(ns[i], cs))

                if self.memory.get(cs) == None:
                    self.memory[cs] = {}

                self.memory[cs][ns[i]] = value

        return value

    # Función de comparación personalizada
    def comparar(self,secuencia):
        # Se considera solo el primer carácter de la secuencia para ordenar
        return (secuencia[1], secuencia[0])

    def validateElementCandidate(self, arrToValidate):
    
        # Ordenar con la función personalizada
        secuencias_ordenadas = sorted(arrToValidate, key=self.comparar, reverse=True)
        
        # Obtener las letras finales de cada secuencia
        letras_finales = [secuencia[1] for secuencia in secuencias_ordenadas]

        # Contar cuántas veces aparece cada letra final
        contador = Counter(letras_finales)

        # Usamos defaultdict para crear un diccionario donde los valores son listas
        groupedSubSeq = defaultdict(list)

        # Agrupar las secuencias según su letra mayúscula final
        for subsecuencia in secuencias_ordenadas:
            letra_final = subsecuencia[1]  # Tomamos la letra mayúscula final
            groupedSubSeq[letra_final].append(subsecuencia)

        # Convertir el diccionario a una lista de sub-arreglos
        sub_arreglos = list(groupedSubSeq.values())

        return sub_arreglos

    def selectedRowCandSys(self, tableMarginalized, varMarginalized):
        
        rowFound = ""

        for i, valor in enumerate(self.cs_value):
            letra = self.candidateSystem[::-1][i]  # Obtenemos la letra correspondiente (A, B, C, ...)
            if(letra != varMarginalized.upper()):
                rowFound +=valor
                #st.text(letra)
                #st.text(valor)
        return tableMarginalized[int(rowFound,2)]

    def generar_combinaciones(self, seleccionados, restantes, Primero):

        st.divider()

        Opciones = []
        Combinacion =[False,1]

        if isinstance(seleccionados,list) and len(seleccionados)>1 and Primero:
            Combinacion[0]=True
            Combinacion[1]=len(seleccionados)

        if not restantes:
                return seleccionados

        for i in range(len(restantes)):
            seleccionados.append(restantes[i])
            Copsel=seleccionados[:]
            Copia = restantes[:]
            Copia.remove(restantes[i])

            if not Copia:
                return seleccionados

            # creo que copsel no debería reescribirse, se debe trabajar com otra variable y dejar Copsel para el manejo de las estrategia de josé 
            myCopsel = self.validateElementCandidate(Copsel)
            marginalizedTable = []
            
            # Arreglo de filas selccionadas a base del valor del estado original
            rowsSystCandSelected = []

            # Calcular la Distancia de Wasserstein (EMD)
            emd_distance = float('inf')

            st.info(f"Inicio de Proceso para {Copsel}")

            for iSubSeq in range(len(myCopsel)):

                for j in range(len(myCopsel[iSubSeq])):
                    subSeqCopsel = myCopsel[iSubSeq][j]

                    if(len(myCopsel[iSubSeq]) > 1):
                        st.warning('Marginalización múltiple detectada', icon="ℹ️")
                        if(j == 0):
                            marginalizedTable.append(self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], self.futureTables['primogenitalTables'][subSeqCopsel[1]],True))
                        else:
                            marginalizedTable.append(self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], marginalizedTable[(len(marginalizedTable) - 1)], False))
                        st.warning('Marginalización múltiple finalizada', icon="✅")
                    else:
                        rawTableMar = self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], self.futureTables['primogenitalTables'][subSeqCopsel[1]])
                        rowsSystCandSelected.append(self.selectedRowCandSys(rawTableMar,subSeqCopsel[0]))
                        marginalizedTable.append(rawTableMar)

            #st.table(marginalizedTable)
            return True
            # Calcular la Distancia de Wasserstein (EMD)
            emd_distance = random.randint(1,100)
                                    
            if (emd_distance > 0.0) and (emd_distance < self.min_emd):
                self.min_emd = emd_distance
                self.mejor_particion = [Copsel,Copia,emd_distance]
                
            st.divider()
            st.subheader(f"EMD Distance: {[Copsel,Copia,emd_distance]}")    
            st.info(f"Final de Proceso para {Copsel}")
            st.divider()

            Opciones.append([Copsel,Copia,emd_distance])
            seleccionados.remove(restantes[i])

        st.subheader("Combinación Elegida",divider="gray")
        st.text(f"{self.mejor_particion[0],self.mejor_particion[1]}")
        seleccion = min(Opciones, key=lambda x: x[2])
        Final= self.generar_combinaciones(seleccion[0], seleccion[1], False)

        if(Combinacion[0]):
            Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
            st.latex(f"{Final}")
        return Final
    
    def strategy(self):
        
        st.header("Combinaciones Encontradas")

        self.cs = ''.join(sorted(self.cs, reverse=True))
        self.ns = ''.join(sorted(self.ns, reverse=True))

        Todos = [''.join(comb) for comb in itertools.product(self.cs, self.ns)]

        st.subheader(f"Procesando {Todos}")

        while len(Todos) > 2:

            Final = self.generar_combinaciones([Todos[0]], Todos[1:], True)
            Arreglo = self.Cortar(Final)
                    
            for x in Todos[3:] :
                st.subheader("--Alejo--",divider="blue")
                self.min_emd = float("inf")
                Arreglo = self.generar_combinaciones(Arreglo[len(Arreglo)-1],Arreglo[:-1],True)
                Arreglo = self.Cortar(Arreglo)
                st.latex(f'{Arreglo}')
                st.latex(rf"""\bullet EMD : {self.min_emd}""")
                st.latex(rf"""\bullet Mejor Combinación : {self.mejor_particion}""")

            Todos = Arreglo

        return self.mejor_particion, round(self.min_emd, 5)
    