from networkx import tensor_product
import numpy as np
import random
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
    impresos = set()

    min_emd = float("inf")
    mejor_particion = None
    emd_distance = float("inf")

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

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Estados Encontrados")

        Todos = []
        
        for x in range(len(ns)):
            Todos.append(ns[x]+"N")
        
        for x in range(len(cs)):
            Todos.append(cs[x])
        #Todos = ["aA","aB","aC","bA","bB","bC","cA","cB","cC"]
        while len(Todos) > 2:
            Final = generar_combinaciones([Todos[0]],Todos[1:],True,st)
            st.latex(f'{Final} - Unido')
            Arreglo = Cortar(Final)
            
            for x in Todos[3:] :
                Arreglo = generar_combinaciones(Arreglo[len(Arreglo)-1],Arreglo[:-1],True,st)
                Arreglo = Cortar(Arreglo)
                st.latex(f'{Arreglo} - Unido')

            Todos = Arreglo

            #st.latex(Todos)

    with col2:
        
        st.subheader("Memoría")

        st.json(memory)

    return mejor_particion, round(min_emd, 5)
    

def generar_combinaciones(seleccionados, restantes,Primero, st):
    st.latex(f"{seleccionados} - {restantes}")
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
        Valor = random.randint(1, 100)
        st.latex(f"{Copsel} - {Copia} - {Valor}")
        Opciones.append([Copsel,Copia,Valor])
        seleccionados.remove(restantes[i])
    st.latex(f'{min(Opciones, key=lambda x: x[2])}')
    seleccion = min(Opciones, key=lambda x: x[2])
    Final= generar_combinaciones(seleccion[0], seleccion[1],False, st)
    if(Combinacion[0]):
        Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
        st.latex(f"{Final}")
    return Final

def  Cortar(Lista):
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