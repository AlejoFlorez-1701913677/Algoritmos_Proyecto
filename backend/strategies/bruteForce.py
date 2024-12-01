import numpy as np
import streamlit as st

from scipy.stats import wasserstein_distance

from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from backend.marginalizacion import obtener_tabla_probabilidades

class BruteForce:

    def __init__(self, probabilities, cs_value, states, cs, ns):
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.memory = {}
        self.states = states
        self.min_emd = float("inf")
        self.mejor_particion = []
        self.impresos = set()

        self.original_system = obtener_tabla_probabilidades(
            repr_current_to_array(cs, cs_value),
            repr_next_to_array(ns),
            probabilities,
            states,
        )

        st.write("Sistema Original")
        st.latex(rf"""\bullet \left(\frac{{{ns}ᵗ⁺¹}}{{{cs}ᵗ}}\right)""")

        original_system = obtener_tabla_probabilidades(
            repr_current_to_array(cs, cs_value),
            repr_next_to_array(ns),
            probabilities,
            states,
        )

        st.write("Validación Estado Original")
        st.text(original_system)


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
    
    def strategy(self,ns, cs):

        st.subheader("Estados Encontrados")

        for lenNs in range(len(ns) + 1):

            for i in range(len(ns) - lenNs + 1):
                j = i + lenNs - 1
                ns1, ns2 = ns[i : j + 1], ns[:i] + ns[j + 1 :]

                for lenCs in range(len(cs) + 1):
                    for x in range(len(cs) - lenCs + 1):
                        z = x + lenCs - 1
                        cs1, cs2 = cs[x : z + 1], cs[:x] + cs[z + 1 :]

                        # Verificar duplicados
                        combinacion_actual = ((ns1, cs1), (ns2, cs2))
                        combinacion_inversa = ((ns2, cs2), (ns1, cs1))

                        if (combinacion_actual not in self.impresos and combinacion_inversa not in self.impresos) or (ns1 == ns and ns2 == "" and cs1 == "" and cs2 == ""):
                            
                            st.latex(rf"""\bullet \left(\frac{{{ns2}}}{{{cs2}}}\right) * \left(\frac{{{ns1}}}{{{cs1}}}\right)""")
                            st.latex(rf"""\bullet \left(\frac{{{ns1}}}{{{cs1}}}\right) * \left(\frac{{{ns2}}}{{{cs2}}}\right)""")
                            
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
                                # No puede tener arreglo vacio
                                emd_distance = wasserstein_distance(self.original_system,partitioned_system)
                                st.latex(rf"""\bullet {emd_distance}""")
                                
                                if emd_distance < self.min_emd and emd_distance > 0:
                                    self.min_emd = emd_distance
                                    mejor_particion = combinacion_actual

                            self.impresos.add(combinacion_actual)
                            self.impresos.add(combinacion_inversa)

        return mejor_particion, round(self.min_emd, 5)