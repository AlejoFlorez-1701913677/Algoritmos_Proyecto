import time

import os
import sys
import json

import streamlit as st
import pandas as pd
from io import StringIO


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from backend.strategies.minimaParticion import decomposition

from backend.generator.probabilities import generatorProbabilities

from backend.candidateSystemGenerator.candidateGenerator import indexCandidateSystem, marginalize_variableFuture, marginalize_variablePresent

def format_partition_output(partition_result):
    # Extraer las particiones de 'ns' y 'cs' junto con la distancia de EMD
    particiones_ns, particiones_cs = partition_result[0]
    distancia_emd = partition_result[1]

    # Formatear las particiones de 'ns' y 'cs' para imprimir
    particiones_ns_formateadas = " | ".join(
        ["".join(subparticion) for subparticion in particiones_ns]
    )
    particiones_cs_formateadas = " | ".join(
        ["".join(subparticion) for subparticion in particiones_cs]
    )

    # Construir y devolver el resultado formateado
    formatted_output = {
        "Particione de ns": particiones_ns_formateadas,
        "Particione de cs": particiones_cs_formateadas,
        "Distancia de EMD": distancia_emd,
    }

    print("\n\n|===========================================================|")
    print("|--- %s Segundos ---" % (time.time() - start_time),"|")
    print("|===========================================================|")

    return formatted_output

st.title('Próyecto Final')
st.subheader('Análisis Y Diseño De Algoritmo')

st.divider()

data = st.file_uploader("Elige un Archivo")

st.divider()

#st.subheader("Descomponer tabla de probabilidad")
#st.page_link("pages/index_Conversion.py",label="Descomponer Tabla de Probabilidad")

if data is not None:

    st.header('Contenido del Documento')
    st.write(pd.read_json(data))

    # To convert to a string based IO:
    dataJson = json.loads(StringIO(data.getvalue().decode("utf-8")).read())

    searchStatus, result_matrix, states, varData = generatorProbabilities(dataJson)

    st.header('Tabla de Probabilidad')
    st.table(result_matrix)

    st.text('Estado Buscado')
    st.text(dataJson["stateSought"])

    st.text('Valor Encontrado')
    st.text(searchStatus)

    st.divider()

    with st.expander("Primera Estrategia"):

        candidateSystem_Perfect = []

        st.divider()

        st.title("¿Desea Crear un sistema Candidato?")

        st.write("Llené los siguientes datos, teniendo en cuenta que solo se puede marginalizar variables que se encuentren continuas")
        candidateSystem = st.text_input("Sistema candidato", "ABC")

        execCandidateSystem = st.button("Obtener sistema candidato")

        if execCandidateSystem:

            candidateSystem_Imperfect = indexCandidateSystem(result_matrix,candidateSystem, varData)
            candidateSystem_Perfect = marginalize_variableFuture(candidateSystem_Imperfect,candidateSystem, varData)
            
            st.subheader("Tabla de Sistema Candidato - Imperfecta")
            st.table(candidateSystem_Imperfect)

            st.subheader("Tabla de Sistema Candidato - Perfecta (Marginalizada)")
            st.table(candidateSystem_Perfect)

            st.divider()

        st.subheader("Subsistema")
        
        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

        sysC_currentStatus = st.text_input("Estado Presente", "")
        sysC_nextStatus = st.text_input("Estado Futuro", "")

        execPairContruction = st.button("Obtener Pares")

        if execPairContruction:

            st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

            mejor_particion, min_emd = decomposition(sysC_nextStatus, sysC_currentStatus, dataJson["stateSought"], result_matrix, states, st)

            st.text(mejor_particion)
            st.text(min_emd)