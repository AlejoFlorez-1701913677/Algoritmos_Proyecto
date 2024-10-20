from networkx import tensor_product
import numpy as np
from scipy.stats import wasserstein_distance

from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from chartPlotter.ProbabilityTransitionController import graphProbability

from backend.marginalizacion import obtener_tabla_probabilidades


def decomposition(ns, cs, cs_value, probabilities, states, st):
    memory = {}

    st.write("Sistema Original")
    st.write(""f"{ns}ᵗ⁺¹ | {cs}ᵗ")

    original_system = obtener_tabla_probabilidades(
        repr_current_to_array(cs, cs_value),
        repr_next_to_array(ns),
        probabilities,
        states,
    )

    st.write("Validación Estado Original")
    st.text(original_system)

    graphProbability(original_system,st)

    memory = {}
    impresos = set()

    min_emd = float("inf")
    mejor_particion = None
    emd_distance = float("inf")

    def descomponer(ns, cs, memory, states):
        if memory.get(cs) is not None and memory.get(cs).get(ns) is not None:
            if any(memory.get(cs).get(ns)):
                return memory.get(cs).get(ns)

        if len(ns) == 1:
            value = obtener_tabla_probabilidades(
                repr_current_to_array(cs, cs_value),
                repr_next_to_array(ns),
                probabilities,
                states,
            )
            return value

        value = []
        for i in range(0, len(ns)):
            if len(value) > 0:
                cross_product = np.kron(value, descomponer(ns[i], cs, memory, states))
                value = ordenar_matriz_product(cross_product)
            else:
                value = np.array(descomponer(ns[i], cs, memory, states))

                if memory.get(cs) == None:
                    memory[cs] = {}

                memory[cs][ns[i]] = value

        return value

    col1, col2 = st.columns(2)

    with col1:

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

                        if (
                            combinacion_actual not in impresos
                            and combinacion_inversa not in impresos
                        ) or (ns1 == ns and ns2 == "" and cs1 == "" and cs2 == ""):
                            
                            st.latex(rf"""
                                     \bullet \left(\frac{{{ns2}}}{{{cs2}}}\right) * \left(\frac{{{ns1}}}{{{cs1}}}\right)
                                     """)
                            
                            arr1 = np.array(descomponer(ns2, cs2, memory, states))
                            arr2 = np.array(descomponer(ns1, cs1, memory, states))

                            partitioned_system = []

                            if len(arr1) > 0 and len(arr2) > 0:
                                cross_product = np.kron(arr1, arr2)
                                partitioned_system = ordenar_matriz_product(cross_product)

                            elif len(arr1) > 0:
                                partitioned_system = arr1
                            elif len(arr2) > 0:
                                partitioned_system = arr2

                            if len(partitioned_system) > 0:
                                # Convertir partitioned_system a array de NumPy si no lo es
                                partitioned_system = np.array(partitioned_system)

                                # Calcular la Distancia de Wasserstein (EMD)
                                emd_distance = wasserstein_distance(
                                    original_system,
                                    partitioned_system,
                                )
                                
                                if emd_distance < min_emd:
                                    min_emd = emd_distance
                                    mejor_particion = combinacion_actual

                            impresos.add(combinacion_actual)
                            impresos.add(combinacion_inversa)

    with col2:
        
        st.subheader("Memoría")

        st.json(memory)


    return mejor_particion, round(min_emd, 5)
    
