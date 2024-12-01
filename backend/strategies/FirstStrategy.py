
import numpy as np
import streamlit as st

from scipy.stats import wasserstein_distance

from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from backend.marginalizacion import obtener_tabla_probabilidades

class FirstStrategy:

    def __init__(self, probabilities, cs_value, states, cs, ns):
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.memory = {}
        self.states = states
        self.min_emd = float("inf")
        self.mejor_particion = []

        self.original_system = obtener_tabla_probabilidades(
            repr_current_to_array(cs, cs_value),
            repr_next_to_array(ns),
            probabilities,
            states,
        )

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
        
        ns1 = [item for item in selected if 'N' in item]
        ns1 = ''.join([item.replace('N', '') for item in ns1])

        cs1 = [item for item in selected if 'N' not in item]
        cs1 = ''.join([item.replace('N', '') for item in cs1])

        ns2 = [item for item in remaining if 'N' in item]
        ns2 = ''.join([item.replace('N', '') for item in ns2])
        
        cs2 = [item for item in remaining if 'N' not in item]
        cs2Result = []
        for item in cs2:
            if isinstance(item, list):
                # Si el item es una lista, aplicamos el reemplazo a cada uno de los elementos dentro de la lista
                cs2Result.append([subitem.replace('N', '') for subitem in item])
            elif isinstance(item, str):
                # Si el item es una cadena, simplemente reemplazamos 'N' por ''
                cs2Result.append(item.replace('N', ''))
            else:
                # Si el item no es ni lista ni cadena, lo dejamos tal cual
                cs2Result.append(item)

        flattened = [str(item) for sublist in cs2Result for item in (sublist if isinstance(sublist, list) else [sublist])]
        st.text(f"-> {''.join(flattened)}")
        st.latex(rf"""\bullet \left(\frac{{{ns1}}}{{{cs1}}}\right) * \left(\frac{{{ns2}}}{{{''.join(flattened)}}}\right)""")
        return ns1,cs1,ns2,''.join(flattened)

    def generar_combinaciones(self, seleccionados, restantes, Primero):

        st.divider()
        st.subheader("Sistema a combinar:",divider="gray")

        st.text(seleccionados)
        st.text(restantes)
        
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
                                
                if (emd_distance > 0.0) and (emd_distance < self.min_emd):
                    self.min_emd = emd_distance
                    self.mejor_particion = [Copsel,Copia,emd_distance]
            
            Opciones.append([Copsel,Copia,emd_distance])
            seleccionados.remove(restantes[i])

        st.text("Combinación Elegida")
        self.formatStrategie(self.mejor_particion[0],self.mejor_particion[1])
        self.min_emd = float("inf")
        
        seleccion = min(Opciones, key=lambda x: x[2])
        Final= self.generar_combinaciones(seleccion[0], seleccion[1], False)

        if(Combinacion[0]):
            Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
            #st.latex(f"{Final}")
        return Final