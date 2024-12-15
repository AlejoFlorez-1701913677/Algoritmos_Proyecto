
import numpy as np
import streamlit as st


from scipy.stats import wasserstein_distance

from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from backend.marginalizacion import obtener_tabla_probabilidades
from backend.candidateSystemGenerator.Marginalization import Marginalization


class FirstStrategy:

    def __init__(self, probabilities, cs_value, states, cs, ns, st2_candidateSystem, varData):
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.memory = {}
        self.states = states
        self.min_emd = float("inf")
        self.mejor_particion = []
        self.cs = cs
        self.ns = ns
        self.marginalization = Marginalization(probabilities,st2_candidateSystem, varData)

        st.write("Sistema Original")
        st.latex(rf"""\bullet \left(\frac{{{self.ns}ᵗ⁺¹}}{{{self.cs}ᵗ}}\right)""")

        candidateSystem_Imperfect = self.marginalization.indexCandidateSystem()
        candidateSystem_Perfect = self.marginalization.marginalize_variableFuture(candidateSystem_Imperfect)
            
        st.subheader("Tabla de Sistema Candidato - Imperfecta")
        st.table(candidateSystem_Imperfect)

        st.subheader("Tabla de Sistema Candidato - Perfecta (Marginalizada)")
        st.table(candidateSystem_Perfect)

        self.original_system = obtener_tabla_probabilidades(
            repr_current_to_array(self.cs, self.cs_value),
            repr_next_to_array(self.ns),
            self.probabilities,
            self.states,
        )

        st.write("Validación Estado Original")
        st.text(self.original_system)

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

    def formatStrategie(self, selected, remaining):

        ns2Result = []
        ns1Result = []
        cs1Result = []
        cs2Result = []

        for item in selected:

            #st.text(f"item -> {item}")
            if isinstance(item, list):
                # Si el item es una lista, procesamos cada elemento dentro de la lista
                for subitem in item:
                    if 'N' in subitem:  # Verificamos si el subelemento contiene 'N'
                        ns1Result.append(subitem.replace('N', ''))  # Elimina 'N' y agrega a ns1Result
                    else:
                        cs1Result.append(subitem)  # Si no tiene 'N', lo agregamos a cs1Result
            elif isinstance(item, str):
                # Si el item es una cadena, verificamos si contiene 'N'
                if 'N' in item:
                    ns1Result.append(item.replace('N', ''))  # Elimina 'N' y agrega a ns1Result
                else:
                    cs1Result.append(item)  # Si no tiene 'N', lo agregamos a cs1Result
            else:
                # Si el item no es ni lista ni cadena, lo dejamos tal cual
                cs1Result.append(item)

        cs1_flattened = [str(item) for sublist in cs1Result for item in (sublist if isinstance(sublist, list) else [sublist])]
        ns1_flattened = [str(item) for sublist in ns1Result for item in (sublist if isinstance(sublist, list) else [sublist])]
        

        for item in remaining:
            if isinstance(item, list):
                # Si el item es una lista, procesamos cada elemento dentro de la lista
                for subitem in item:
                    if 'N' in subitem:  # Verificamos si el subelemento contiene 'N'
                        ns2Result.append(subitem.replace('N', ''))  # Elimina 'N' y agrega a ns1Result
                    else:
                        cs2Result.append(subitem)  # Si no tiene 'N', lo agregamos a cs1Result
            elif isinstance(item, str):
                # Si el item es una cadena, verificamos si contiene 'N'
                if 'N' in item:
                    ns2Result.append(item.replace('N', ''))  # Elimina 'N' y agrega a ns1Result
                else:
                    cs2Result.append(item)  # Si no tiene 'N', lo agregamos a cs1Result
            else:
                # Si el item no es ni lista ni cadena, lo dejamos tal cual
                cs2Result.append(item)

        cs2_flattened = [str(item) for sublist in cs2Result for item in (sublist if isinstance(sublist, list) else [sublist])]
        ns2_flattened = [str(item) for sublist in ns2Result for item in (sublist if isinstance(sublist, list) else [sublist])]


        st.latex(rf"""\bullet \left(\frac{{{''.join(ns1_flattened)}}}{{{''.join(cs1_flattened)}}}\right) * \left(\frac{{{''.join(ns2_flattened)}}}{{{''.join(cs2_flattened)}}}\right)""")
        return ''.join(ns1_flattened),''.join(cs1_flattened),''.join(ns2_flattened),''.join(cs2_flattened)

    def generar_combinaciones(self, seleccionados, restantes, Primero):
        self.min_emd = float("inf")
        st.divider()
        st.subheader("Sistema a combinar:",divider="gray")
        
        self.formatStrategie(seleccionados,restantes)

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

            ns1,cs1,ns2,cs2 = self.formatStrategie(Copsel,Copia)

            arr1 = np.array(self.descomponer(ns2, cs2))
            arr2 = np.array(self.descomponer(ns1, cs1))

            partitioned_system = []
            
            if len(arr1) > 0:
                partitioned_system = arr1

            if len(arr2) > 0:
                partitioned_system = arr2

            if len(arr1) > 0 and len(arr2) > 0:
                cross_product = np.kron(arr1, arr2)
                partitioned_system = ordenar_matriz_product(cross_product)

            if len(partitioned_system) > 0:
                
                # Convertir partitioned_system a array de NumPy si no lo es
                partitioned_system = np.array(partitioned_system)

                # Calcular la Distancia de Wasserstein (EMD)
                emd_distance = wasserstein_distance(self.original_system,partitioned_system)
                st.latex(rf"""\bullet EMD : {emd_distance}""")
                                
                if (emd_distance >= 0.0) and (emd_distance < self.min_emd):
                    self.min_emd = emd_distance
                    self.mejor_particion = [Copsel,Copia,emd_distance]
            
            Opciones.append([Copsel,Copia,emd_distance])
            seleccionados.remove(restantes[i])

        st.subheader("Combinación Elegida",divider="gray")
        self.formatStrategie(self.mejor_particion[0],self.mejor_particion[1])
        
        seleccion = min(Opciones, key=lambda x: x[2])
        Final= self.generar_combinaciones(seleccion[0], seleccion[1], False)

        if(Combinacion[0]):
            Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
            #st.latex(f"{Final}")
        return Final
    
    def strategy(self, ):
        
        st.header("Combinaciones Encontradas")

        Todos = []
                
        for x in range(len(self.ns)):
            Todos.append(self.ns[x]+'N')
                
        for x in range(len(self.cs)):
            Todos.append(self.cs[x])

        while len(Todos) > 2:

            Final = self.generar_combinaciones([Todos[0]], Todos[1:], True)
            st.latex(f'{Final}')
            Arreglo = self.Cortar(Final)
                    
            for x in Todos[3:] :
                self.min_emd = float("inf")
                Arreglo = self.generar_combinaciones(Arreglo[len(Arreglo)-1],Arreglo[:-1],True)
                Arreglo = self.Cortar(Arreglo)
                self.formatStrategie(Arreglo[0],Arreglo[1])
                st.latex(f'{Arreglo}')
                st.latex(rf"""\bullet EMD : {self.min_emd}""")
                st.latex(rf"""\bullet Mejor Combinación : {self.mejor_particion}""")

            Todos = Arreglo

        return self.mejor_particion, round(self.min_emd, 5)
    