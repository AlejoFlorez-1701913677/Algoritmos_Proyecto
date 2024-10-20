import numpy as np


# Obtiene la tabla eliminado las filas  que no se encuentre en el parametro de candidateSystem (Cuando el valor binario de la variable es 1)
def indexCandidateSystem_v4(probabilities, candidateSystem, full_system):
    
    # Encontrar las variables faltantes
    missing_variables = [var for var in full_system if var not in candidateSystem]
    
    # Tamaño de la matriz
    size = len(probabilities)
    num_variables = len(full_system)
    
    # Crear una lista para almacenar las filas que no se deben eliminar
    valid_rows = []

    # probabilidades resultantes
    probabilities_result = []
    
    for i in range(size):
        # Generar la representación binaria de la fila actual
        # Al crear el formato en binario, se reescribe al reves, esto para que la validación de valor en la posición sea correcta
        row_binary = format(i, f'0{num_variables}b')[::-1]
        
        # Revisar si las posiciones de las variables faltantes tienen un "1"
        should_remove = False
        for j, missing_var in enumerate(missing_variables):
            # Chequear el bit correspondiente a la variable faltante
            # El bit más significativo (izquierda) es el primer bit en row_binary
            # Encontramos el índice correcto de la variable faltante en la representación binaria
            missing_var_index = full_system.index(missing_var)  # El índice en full_system de la variable faltante
            #print(row_binary + " -> "+missing_var+" :: "+str(missing_var_index)+" ::: "+row_binary[missing_var_index])
            if row_binary[missing_var_index] == "1":  # Si ese bit es 1, eliminamos la fila
                should_remove = True
                break
        
        #print(f'{row_binary}: {probabilities[i]}')
        
        # Si no hay un "1" en la posición de las variables faltantes, conservar la fila
        if not should_remove:
            #print("--> "+row_binary)
            #print(probabilities[i])
            valid_rows.append(probabilities[i])
    
    # Imprimir las filas válidas con sus representaciones binarias
    for idx, row in enumerate(valid_rows):
        row_binary = format(idx, f'0{len(candidateSystem)}b')
        #print(f'{row_binary}: {row}')
        probabilities_result.append(row)

    #print("-----------------------------------------------")
    return probabilities_result

# Obtiene la tabla eliminado las filas  que no se encuentre en el parametro de candidateSystem (Cuando el valor binario de la variable es 1)
# Sumo las columnas que las variables del sistema candidato sean iguales, pero la variable eliminada sea distinta
# ((v1+v2)/2)
# retorna una tabla de 3x3 (al ser 4 variables)
def marginalizationTable_v4(probabilities, candidateSystem, full_system):
     
    num_variables_full = len(full_system)
    num_variables_candidate = len(candidateSystem)
    
    # Identificar la variable faltante
    missing_variable = [var for var in full_system if var not in candidateSystem]
    
    if not missing_variable:
        print("No missing variables. Returning original table.")
        return probabilities  # No hay variables faltantes, no es necesario multiplicar
    
    missing_variable = missing_variable[0]  # Asumimos que solo falta una variable

    # Crear una tabla vacía con las mismas dimensiones que la original
    result_table = [[0] * len(probabilities[0]) for _ in range(len(probabilities))]
    
    # Número de columnas en la tabla
    num_columns = len(probabilities[0]) if probabilities else 0
    
    # Recorrer las columnas de la tabla y procesar las que solo difieren en la variable faltante
    for i in range(num_columns):
        # Generar la representación binaria de la columna actual
        col_binary = format(i, f'0{num_variables_full}b')
        
        # Si la posición de la variable faltante es 0, buscamos la columna que difiere solo en esa variable
        if col_binary[full_system.index(missing_variable)] == "0":
            # Generar el índice de la columna "gemela" que difiere solo en la variable faltante
            twin_index = i + (1 << (num_variables_full - full_system.index(missing_variable) - 1))  # Cambia el bit de la variable faltante
            
            # Multiplicar las columnas i y twin_index
            for row in range(len(probabilities)):
                result_table[row][i] = ((probabilities[row][i] * probabilities[row][twin_index])/2)
    
    # Crear una nueva tabla sin las columnas cuyo índice de la variable faltante sea 1
    final_table = []
    
    for row in result_table:
        # Filtrar las columnas donde el bit correspondiente a la variable faltante sea 0
        filtered_row = [row[i] for i in range(num_columns) if format(i, f'0{num_variables_full}b')[full_system.index(missing_variable)] == "0"]
        final_table.append(filtered_row)
    
    # Imprimir la nueva tabla después de la multiplicación y eliminación
    #for row in final_table:
        #print(row)

    # Retornar la tabla final (n x n)
    return final_table
    # return []
