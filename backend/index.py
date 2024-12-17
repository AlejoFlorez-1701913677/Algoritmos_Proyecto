import time
import csv
import os
import sys
import json
import itertools

import streamlit as st
import pandas as pd
from io import StringIO


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from backend.strategies.bruteForce import BruteForce
from backend.strategies.FirstStrategy import FirstStrategy
from backend.strategies.SecondStrategy import SecondStrategy
from backend.strategies.ThirdStrategy import ThirdStrategy

from backend.generator.probabilities import generatorProbabilities

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

    with st.expander("Fuerza Bruta"):

        sysFB_candidateSystem_Perfect = []

        st.divider()

        st.title("¿Desea Crear un sistema Candidato?")

        st.write("Llené los siguientes datos, teniendo en cuenta que solo se puede marginalizar variables que se encuentren continuas")
        sysFB_candidateSystem = st.text_input("Sistema candidato - Fuerza Bruta", "ABC")

        st.subheader("Subsistema")
        
        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

        sysFB_currentStatus = st.text_input("Estado Presente - Fuerza Bruta", "")
        sysFB_nextStatus = st.text_input("Estado Futuro - Fuerza Bruta", "")

        sysFB_execPairContruction = st.button("Obtener Pares - Fuerza Bruta")

        # Crear una lista para guardar todas las combinaciones
        all_combinations = []

        # Recorrer todas las longitudes posibles de combinación entre 1 y len(cs)
        for i in range(1, len(sysFB_currentStatus) + 1):
            for j in range(1, len(sysFB_nextStatus) + 1):
                # Obtener combinaciones de tamaño i de cs y tamaño j de ns
                for comb_cs in itertools.combinations(sysFB_currentStatus, i):
                    for comb_ns in itertools.combinations(sysFB_nextStatus, j):
                        if(len(comb_cs)+len(comb_ns)>=3):
                            all_combinations.append((''.join(comb_cs), ''.join(comb_ns)))

        # Mostrar todas las combinaciones
        st.subheader(f" Combinaciones encontradas {len(all_combinations)}",divider="blue")
        ElementosGuardar = []
        
        if sysFB_execPairContruction:

            st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")
            
            for x in range(len(all_combinations)):
                bruteForce = BruteForce(result_matrix, dataJson["stateSought"], states, all_combinations[x][0], all_combinations[x][1], dataJson, sysFB_candidateSystem, varData)
                FB_mejor_particion, FB_min_emd,Tiempo = bruteForce.strategy(all_combinations[x][1], all_combinations[x][0])
                #st.subheader(f"Resultado numero {x+1}")
                #st.subheader(f"Mejor Partición encontrada {FB_mejor_particion}")
                #st.subheader(f"Mejor EMD {FB_min_emd}",divider="gray")
                ElementosGuardar.append({"Sistema":all_combinations[x],"combination":FB_mejor_particion, "emd":str(FB_min_emd),"Tiempo":Tiempo})
        
        with open('archivo.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Escribir el encabezado del CSV
            writer.writerow(['combination', 'emd','System', 'Tiempo'])
            
            # Iterar sobre el arreglo de objetos y escribir cada fila
            for obj in ElementosGuardar:
                # Convertir las tuplas de combination a una cadena (puedes elegir el formato que más te convenga)
                combination_str = '; '.join([f"({x[0]}, {x[1]})" for x in obj['combination']])
                
                # Convertir el valor de 'emd' a string
                emd_str = str(obj['emd'])

                sistema = str(obj["Sistema"])
                
                # Escribir la fila en el CSV
                writer.writerow([combination_str, emd_str,sistema,str(obj["Tiempo"])])


        st.subheader("Finalización de Estrategia",divider="blue")

    with st.expander("Primera Estrategia"):

        candidateSystem_Perfect = []

        st.divider()

        st.title("¿Desea Crear un sistema Candidato?")

        st.write("Llené los siguientes datos, teniendo en cuenta que solo se puede marginalizar variables que se encuentren continuas")
        candidateSystem = st.text_input("Sistema candidato", "ABC")

        st.subheader("Subsistema")
        
        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

        sysC_currentStatus = st.text_input("Estado Presente", "")
        sysC_nextStatus = st.text_input("Estado Futuro", "")

        execPairContruction = st.button("Obtener Pares")

        # Crear una lista para guardar todas las combinaciones
        all_combinations = []

        # Recorrer todas las longitudes posibles de combinación entre 1 y len(cs)
        for i in range(1, len(sysC_currentStatus) + 1):
            for j in range(1, len(sysC_nextStatus) + 1):
                # Obtener combinaciones de tamaño i de cs y tamaño j de ns
                for comb_cs in itertools.combinations(sysC_currentStatus, i):
                    for comb_ns in itertools.combinations(sysC_nextStatus, j):
                        if(len(comb_cs)+len(comb_ns)>=3):
                            all_combinations.append((''.join(comb_cs), ''.join(comb_ns)))

        # Mostrar todas las combinaciones
        st.subheader(f" Combinaciones encontradas {len(all_combinations)}",divider="green")
        fs_savedElemets = []

        if execPairContruction:

            st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

            for x in range(len(all_combinations)):
                firstStrategy = FirstStrategy(result_matrix, dataJson["stateSought"], states, all_combinations[x][0], all_combinations[x][1], candidateSystem, varData)
                mejor_particion, min_emd, elapsed_time = firstStrategy.strategy(all_combinations[x][1],all_combinations[x][0])
                #st.latex(f"Mejor Caso {mejor_particion} - {min_emd}")
                fs_savedElemets.append({"Sistema":all_combinations[x],"combination":mejor_particion, "emd":str(min_emd),"Tiempo":elapsed_time})


        with open('Strategie1.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Escribir el encabezado del CSV
            writer.writerow(['combination', 'emd','System', 'Tiempo'])
            
            # Iterar sobre el arreglo de objetos y escribir cada fila
            for obj in fs_savedElemets:
                # Convertir las tuplas de combination a una cadena (puedes elegir el formato que más te convenga)
                combination_str = '; '.join([f"({x})" for x in obj['combination']])
                
                # Convertir el valor de 'emd' a string
                emd_str = str(obj['emd'])

                sistema = str(obj["Sistema"])
                
                # Escribir la fila en el CSV
                writer.writerow([combination_str, emd_str,sistema,str(obj["Tiempo"])])

        st.subheader("Finalización de Estrategia",divider="green")

    with st.expander("Segunda Estrategia"):

        st.divider()

        st.title("¿Desea Crear un sistema Candidato?")

        st.write("Llené los siguientes datos, teniendo en cuenta que solo se puede marginalizar variables que se encuentren continuas")
        st2_candidateSystem = st.text_input("Sistema candidato - Estrategia 2", "ABC")

        st.subheader("Subsistema")
        
        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

        st2_sysC_currentStatus = st.text_input("Estado Presente - Estrategia 2", "bc")
        st2_sysC_nextStatus = st.text_input("Estado Futuro - Estrategia 2", "AB")

        st2_execPairContruction = st.button("Obtener Pares - Estrategia 2")

        if st2_execPairContruction:
            st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

            secondtStrategy = SecondStrategy(result_matrix, dataJson["stateSought"], states, st2_sysC_currentStatus, st2_sysC_nextStatus, dataJson, st2_candidateSystem, varData)
            mejor_particion, min_emd = secondtStrategy.strategy()

    # with st.expander("Tercera Estrategia"):

    #     st3_candidateSystem_Perfect = []

    #     st.divider()

    #     st.title("¿Desea Crear un sistema Candidato?")

    #     st.write("Llené los siguientes datos, teniendo en cuenta que solo se puede marginalizar variables que se encuentren continuas")
    #     st3_candidateSystem = st.text_input("Sistema candidato - Estrategia 3", "ABC")

    #     # st3_execCandidateSystem = st.button("Obtener sistema candidato - Estrategia 3")

    #     # if st3_execCandidateSystem:

    #     #     st3_candidateSystem_Imperfect = indexCandidateSystem(result_matrix,st3_candidateSystem, varData)
    #     #     st3_candidateSystem_Perfect = marginalize_variableFuture(st3_candidateSystem_Imperfect,st3_candidateSystem, varData)
            
    #     #     st.subheader("Tabla de Sistema Candidato - Imperfecta")
    #     #     st.table(st3_candidateSystem_Imperfect)

    #     #     st.subheader("Tabla de Sistema Candidato - Perfecta (Marginalizada)")
    #     #     st.table(st3_candidateSystem_Perfect)

    #     #     st.divider()

    #     st.subheader("Subsistema")
        
    #     st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

    #     st3_sysC_currentStatus = st.text_input("Estado Presente - Estrategia 3", "")
    #     st3_sysC_nextStatus = st.text_input("Estado Futuro - Estrategia 3", "")

    #     st3_execPairContruction = st.button("Obtener Pares - Estrategia 3")

    #     if st3_execPairContruction:

    #         st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

    #         thirdStrategy = ThirdStrategy(result_matrix, dataJson["stateSought"], states, sysC_currentStatus, sysC_nextStatus)
    #         mejor_particion, min_emd = thirdStrategy.strategy()

    with st.expander("Tercera Estrategia"):

        st3_candidateSystem_Perfect = []

        st.divider()

        st.title("¿Desea Crear un sistema Candidato?")

        st.write("Llené los siguientes datos, teniendo en cuenta que solo se puede marginalizar variables que se encuentren continuas")
        st3_candidateSystem = st.text_input("Sistema candidato - Estrategia 3", "ABC")

        st.subheader("Subsistema")
        
        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec dignissim nulla. Proin porta nulla eros, ac posuere nisi molestie et. Nulla dapibus pellentesque enim, at elementum nulla mollis ut. Nunc convallis ultricies augue faucibus sagittis. Mauris hendrerit lorem a nunc porta dignissim. Sed vehicula.")

        st3_sysC_currentStatus = st.text_input("Estado Presente - Estrategia 3", "")
        st3_sysC_nextStatus = st.text_input("Estado Futuro - Estrategia 3", "")

        st3_execPairContruction = st.button("Obtener Pares - Estrategia 3")

        if st3_execPairContruction:

            # Instanciar y ejecutar Tercera Estrategia
            try:
                
                #thirdStrategy = ThirdStrategy(result_matrix, dataJson["stateSought"], states, st3_sysC_currentStatus, st3_sysC_nextStatus,candidate_system_input, variable_data)
                third_strategy = ThirdStrategy(
                    probabilities=result_matrix,
                    cs_value=dataJson["stateSought"],
                    states=states,
                    ns=st3_sysC_nextStatus,
                    cs=st3_sysC_currentStatus
                )

                # Ejecutar la estrategia con ACO
                st.caption("Iniciando optimización con ACO para la Tercera Estrategia...")
                best_partition, best_emd = third_strategy.run_aco()

                # Mostrar resultados
                st.success("Resultados obtenidos:")
                st.text(f"Mejor Partición: {best_partition}")
                st.text(f"EMD Mínimo: {best_emd}")

            except Exception as e:
                st.error(f"Ocurrió un error al ejecutar la Tercera Estrategia: {str(e)}")
