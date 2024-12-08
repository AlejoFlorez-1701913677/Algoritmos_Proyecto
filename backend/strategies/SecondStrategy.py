import random
import itertools
import numpy as np
import pandas as pd
import streamlit as st

from backend.candidateSystemGenerator.Marginalization import Marginalization

from backend.auxiliares import (
    ordenar_matriz_product,
    repr_current_to_array,
    repr_next_to_array,
)

from backend.candidateSystemGenerator.candidateGenerator import marginalize_variablePresent, indexCandidateSystem

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
        self.futureTables = futureTables
        self.marginalization = Marginalization(probabilities,st2_candidateSystem, varData)

        self.original_system = obtener_tabla_probabilidades(
            repr_current_to_array(self.cs, self.cs_value),
            repr_next_to_array(self.ns),
            self.probabilities,
            self.states,
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

            # Calcular la Distancia de Wasserstein (EMD)
            emd_distance = random.randint(1,100)
                                
            if (emd_distance > 0.0) and (emd_distance < self.min_emd):
                self.min_emd = emd_distance
                self.mejor_particion = [Copsel,Copia,emd_distance]
            
            st.text(f"{[Copsel,Copia,emd_distance]}")

            for j in range(len(Copsel)):
                self.marginalization.marginalize_variablePresent(Copsel[j][0], Copsel[j][1], self.futureTables['primogenitalTables'][Copsel[j][1]])
                st.divider()
                st.divider()

            Opciones.append([Copsel,Copia,emd_distance])
            seleccionados.remove(restantes[i])
        return True

        st.subheader("Combinación Elegida",divider="gray")
        st.text(f"{self.mejor_particion[0],self.mejor_particion[1]}")
        seleccion = min(Opciones, key=lambda x: x[2])
        Final= self.generar_combinaciones(seleccion[0], seleccion[1], False)

        if(Combinacion[0]):
            Final=[Final[:Combinacion[1]]]+Final[Combinacion[1]:]
            st.latex(f"{Final}")
        return Final
    
    def strategy(self, ):
        
        st.header("Combinaciones Encontradas")

        Todos = [''.join(comb) for comb in itertools.product(self.cs, self.ns)]

        st.text(f"{Todos}")

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
    