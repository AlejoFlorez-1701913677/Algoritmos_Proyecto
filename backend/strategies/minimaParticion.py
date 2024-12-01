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

from backend.strategies.FirstStrategy import FirstStrategy


def decomposition(ns, cs, cs_value, probabilities, states, st):

    firstStrategy = FirstStrategy(probabilities, cs_value, states, cs, ns)

    min_emd = float("inf")
    mejor_particion = None

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

    st.header("Combinaciones Encontradas")

    Todos = []
            
    for x in range(len(ns)):
        Todos.append(ns[x]+'N')
            
    for x in range(len(cs)):
        Todos.append(cs[x])

    while len(Todos) > 2:

        Final = firstStrategy.generar_combinaciones([Todos[0]], Todos[1:], True)
        st.latex(f'{Final}')
        Arreglo = firstStrategy.Cortar(Final)
                
        for x in Todos[3:] :
            Arreglo = firstStrategy.generar_combinaciones(Arreglo[len(Arreglo)-1],Arreglo[:-1],True)
            Arreglo = firstStrategy.Cortar(Arreglo)
            st.latex(f'{Arreglo}')

        Todos = Arreglo

        st.text(len(Todos))

    return mejor_particion, round(min_emd, 5)
    