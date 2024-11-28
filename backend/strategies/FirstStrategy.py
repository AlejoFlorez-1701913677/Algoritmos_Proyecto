import random
import numpy as np
import streamlit as st


from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from backend.marginalizacion import obtener_tabla_probabilidades

class FirstStrategy:

    def __init__(self, probabilities, cs_value):
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.memory = {}
        pass

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
    
    def descomponer(self, ns, cs, states):
        if self.memory.get(cs) is not None and self.memory.get(cs).get(ns) is not None:
            if any(self.memory.get(cs).get(ns)):
                return self.memory.get(cs).get(ns)

        if len(ns) == 1:
            value = obtener_tabla_probabilidades(
                repr_current_to_array(cs, self.cs_value),
                repr_next_to_array(ns),
                self.probabilities,
                states,
            )
            return value

        value = []
        for i in range(0, len(ns)):
            if len(value) > 0:
                cross_product = np.kron(value, self.descomponer(ns[i], cs, self.memory, states))
                value = ordenar_matriz_product(cross_product)
            else:
                value = np.array(self.descomponer(ns[i], cs, self.memory, states))

                if self.memory.get(cs) == None:
                    self.memory[cs] = {}

                self.memory[cs][ns[i]] = value

        return value

    def generar_combinaciones(self, seleccionados, restantes, Primero):

        st.text(seleccionados)

        st.latex(f"{seleccionados} o-o {restantes}")

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

            st.latex(fr"{Copsel} - {Copia} - {Valor}")
            Opciones.append([Copsel,Copia,Valor])
            seleccionados.remove(restantes[i])

        st.latex(f'{min(Opciones, key=lambda x: x[2])}')
        
        seleccion = min(Opciones, key=lambda x: x[2])
        Final= self.generar_combinaciones(seleccion[0], seleccion[1], False)

        if(Combinacion[0]):
            Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
            st.latex(f"{Final}")
        return Final