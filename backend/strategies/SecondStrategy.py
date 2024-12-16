import random
import itertools
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import wasserstein_distance


from collections import Counter, defaultdict

from Bipartido.Bipartido import Graph

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
        self.fullSystem = varData
        self.candidateSystem = st2_candidateSystem
        self.futureTables = futureTables
        self.marginalization = Marginalization(probabilities,st2_candidateSystem, varData)

        st.write("Estado Original")
        st.text(f"{self.cs_value}")

        st2_candidateSystem_Imperfect = self.marginalization.indexCandidateSystem()
        st2_candidateSystem_Perfect = self.marginalization.marginalize_variableFuture(st2_candidateSystem_Imperfect)

        st.subheader("Tabla de Sistema Candidato - Imperfecta")
        st.table(st2_candidateSystem_Imperfect)

        st.subheader("Tabla de Sistema Candidato - Perfecta (Marginalizada)")
        st.table(st2_candidateSystem_Perfect)

        st.text((int(self.cs_value, 2)))
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

    def flatten_array(self, arr):
        # Resultado que almacenará el arreglo aplanado
        result = []
        
        # Recorremos cada elemento del arreglo original
        for item in arr:
            if isinstance(item, list):  # Si el elemento es un sub-arreglo
                result.extend(self.flatten_array(item))  # Llamamos recursivamente para aplanarlo
            else:
                result.append(item)  # Si no es un sub-arreglo, lo agregamos tal cual
        
        return result

    def validateElementCandidate(self, arrToValidate):

        arrToValidate = self.flatten_array(arrToValidate)
    
        # Ordenar con la función personalizada
        secuencias_ordenadas = sorted(arrToValidate, key=self.comparar, reverse=True)
        
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

        #st.subheader(f" csValue {varMarginalized}",divider="orange")

        for i, valor in enumerate(self.cs_value):

            letra = self.fullSystem[i]  # Obtenemos la letra correspondiente (A, B, C, ...)
            if(letra not in varMarginalized.upper()):
                rowFound +=valor
                #st.text(letra)
                #st.text(valor)

        #st.divider()
        #st.subheader(f"Fila Buscada {int(rowFound,2)}",divider="orange")
        return tableMarginalized[int(rowFound,2)]

    def opeEMD(self, rowsSystCandSelected):

        orderedObj = {k: rowsSystCandSelected[k] for k in sorted(rowsSystCandSelected)}
        rowsSystCandOrdered = []

        for key in orderedObj:
            rowsSystCandOrdered.append(orderedObj[key])

        # Inicializamos la lista de resultados
        result = []
        
        # Crear todas las combinaciones posibles de los índices
        # Tomamos un elemento de cada fila (de las dos columnas)
        combinaciones = list(itertools.product(*rowsSystCandOrdered))
        
        # Multiplicamos los elementos de cada combinación
        for combinacion in combinaciones:
            resultado = 1
            for elem in combinacion:
                resultado *= elem
            result.append(resultado)

        return result
    
    def calculateEMD(self, futureNoMarginalized, rowsSystCandSelected):

        rowsSystCandSelectedOpe2 = {}
    
        for rowSysCandSelect in range(len(futureNoMarginalized)):
            rowsSystCandSelectedOpe2[futureNoMarginalized[rowSysCandSelect]] = rowsSystCandSelected[futureNoMarginalized[rowSysCandSelect]]

        missing_vars = list(set(self.candidateSystem) - set(futureNoMarginalized))

        #st.subheader(f" futureNoMarginalized {futureNoMarginalized} - missing_vars {missing_vars}",divider="orange")
        
        for missingVar in range(len(missing_vars)):
            varFuture = missing_vars[::-1][missingVar]

            #st.subheader(f" varFuture {varFuture}")
            #st.table(self.futureTables['primogenitalTables'][varFuture])

            rowsSystCandSelectedOpe2[varFuture] = self.selectedRowCandSys(self.marginalization.reOrderArray(self.futureTables['primogenitalTables'][varFuture]),futureNoMarginalized)

            #st.text(" rowsCandidate")
            #st.table(rowsSystCandSelectedOpe2)

        #st.text("EMD Operando")
        #st.table(self.opeEMD(rowsSystCandSelectedOpe2))
        return self.opeEMD(rowsSystCandSelectedOpe2)

    def generar_combinaciones(self, seleccionados, restantes, Primero,Todos):

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
            rowsSystCandSelected = {}

            futureNoMarginalized = ""

            # Tabla Marginalizada Cruda.
            rawTableMar = []

            # Validación de Variables ya Marginalizadas
            marginalizedVars = ""

            st.info(f"Inicio de Proceso para {Copsel} - {myCopsel}")

            for iSubSeq in range(len(myCopsel)):

                for j in range(len(myCopsel[iSubSeq])):
                    subSeqCopsel = myCopsel[iSubSeq][j]
                    
                    futureNoMarginalized += subSeqCopsel[1]

                    if(len(myCopsel[iSubSeq]) > 1):
                        st.warning('Marginalización múltiple detectada', icon="ℹ️")

                        #Marginalización - Primera iteración
                        if(j == 0):
                            rawTableMar = self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], self.futureTables['primogenitalTables'][subSeqCopsel[1]],True)

                        #Marginalización - última iteración
                        elif (j == (len(myCopsel[iSubSeq]) -1)):
                            rawTableMar = self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], marginalizedTable[(len(marginalizedTable) - 1)], False)
                            rowsSystCandSelected[subSeqCopsel[1]] = self.selectedRowCandSys(rawTableMar,marginalizedVars+subSeqCopsel[0])

                        #Marginalización - Caso Promedio
                        else:
                            rawTableMar = self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], marginalizedTable[(len(marginalizedTable) - 1)], False)
                        
                        marginalizedVars += subSeqCopsel[0]

                        st.warning('Marginalización múltiple finalizada', icon="✅")
                    else:
                        rawTableMar = self.marginalization.marginalize_variablePresent(subSeqCopsel[0], subSeqCopsel[1], self.futureTables['primogenitalTables'][subSeqCopsel[1]])
                        rowsSystCandSelected[subSeqCopsel[1]] = self.selectedRowCandSys(rawTableMar,subSeqCopsel[0])
                    
                    marginalizedTable.append(rawTableMar)

            #st.text("Tabla Sys Can Selected")
            #st.table(rowsSystCandSelected) 
            
            # Revisar Calculo EMD con Variables faltantes dinamicos
            op1EmdDistance = wasserstein_distance(self.original_system,self.calculateEMD(futureNoMarginalized, rowsSystCandSelected))
            op2EmdDistance = wasserstein_distance(self.original_system,self.calculateEMD(myCopsel[iSubSeq][0][1], rowsSystCandSelected))

            # Calcular la Distancia de Wasserstein (EMD)
            emd_distance = op1EmdDistance - op2EmdDistance

            st.warning(f"El calculo de EMD es {emd_distance}")
                                    
            if (emd_distance >= 0.0) and (emd_distance < self.min_emd):
                self.min_emd = emd_distance
                self.mejor_particion = [Copsel,Copia,emd_distance]
                
            st.info(f"Final de Proceso para {Copsel}")
            st.divider()
            st.divider()

            Grafo = Graph()
            for arista in Todos:
                Grafo.add_node(arista[0])
                Grafo.add_node(arista[1])
                Grafo.add_edge(arista[0],arista[1])
                
            for arista in Copsel:
                Grafo.remove_edge(arista[0],arista[1])

            if Grafo.has_bipartition():
                st.latex(rf"""\bullet No Tiene Biparticion""")
            else:
                st.latex(rf"""\bullet Tiene Biparticion""")
            Opciones.append([Copsel,Copia,emd_distance])
            seleccionados.remove(restantes[i])

        st.subheader("Combinación Elegida",divider="gray")
        #st.text(f"{self.mejor_particion[0],self.mejor_particion[1]}")
        seleccion = min(Opciones, key=lambda x: x[2])
        Final= self.generar_combinaciones(seleccion[0], seleccion[1], False,Todos)

        if(Combinacion[0]):
            Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
            st.latex(f"{Final}")
        return Final
    
    def strategy(self):
        
        st.header("Combinaciones Encontradas")

        Grafo = Graph()

        self.cs = ''.join(sorted(self.cs, reverse=True))
        self.ns = ''.join(sorted(self.ns, reverse=True))

        Todos = [''.join(comb) for comb in itertools.product(self.cs, self.ns)]

        st.subheader(f"Procesando {Todos}")

        while len(Todos) > 2:

            Final = self.generar_combinaciones([Todos[0]], Todos[1:], True,Todos)
            Arreglo = self.Cortar(Final)

            for arista in Todos:
                    Grafo.add_node(arista[0])
                    Grafo.add_node(arista[1])
                    Grafo.add_edge(arista[0],arista[1])
                
            for arista in self.mejor_particion[0]:
                    Grafo.remove_edge(arista[0],arista[1])

            if Grafo.has_bipartition():
                st.latex(rf"""\bullet No Tiene Biparticion""")
            else:
                st.latex(rf"""\bullet Tiene Biparticion""")
                    
            for x in Todos[3:] :
                st.subheader("Estrategia 2 - Parte 2",divider="blue")
                self.min_emd = float("inf")
                Arreglo = self.generar_combinaciones(Arreglo[len(Arreglo)-1],Arreglo[:-1],True,Todos)
                Arreglo = self.Cortar(Arreglo)
                st.latex(f'{Arreglo}')
                st.latex(rf"""\bullet EMD : {self.min_emd}""")
                st.latex(rf"""\bullet Mejor Combinación : {self.mejor_particion}""")
                
                for arista in Todos:
                    Grafo.add_node(arista[0])
                    Grafo.add_node(arista[1])
                    Grafo.add_edge(arista[0],arista[1])
                
                for arista in self.mejor_particion[0]:
                    Grafo.remove_edge(arista[0],arista[1])

                if Grafo.has_bipartition():
                    st.latex(rf"""\bullet No Tiene Biparticion""")
                else:
                    st.latex(rf"""\bullet Tiene Biparticion""")
            

            Todos = Arreglo

        return self.mejor_particion, round(self.min_emd, 5)
    