import streamlit as st

from scipy.stats import wasserstein_distance

class Marginalization:

    def __init__(self,probabilities, candidateSystem, fullSystem):
        self.probabilities = probabilities
        self.candidateSystem = candidateSystem
        self.fullSystem = fullSystem
        

    def cut(self,tableCut):

        # Dimensiones de la tabla original
        row = len(tableCut)

        # Crear una lista para almacenar las filas que no se deben eliminar
        valid_rows = []

        # probabilidades resultantes
        probabilities_result = []

        # Identificar la variable faltante
        missingVar = [var for var in self.fullSystem if var not in self.candidateSystem]
        
        if len(missingVar) != 1:
            raise ValueError("Debe faltar solo una variable en el sistema candidato.")


        for i in range(row):
            # Generar la representación binaria de la fila actual
            # Al crear el formato en binario, se reescribe al reves, esto para que la validación de valor en la posición sea correcta
            row_binary = format(i, f'0{len(self.fullSystem)}b')[::-1]

            # Revisar si las posiciones de las variables faltantes tienen un "1"
            should_remove = False

            for j, missing_var in enumerate(missingVar):
                 # Chequear el bit correspondiente a la variable faltante
                # El bit más significativo (izquierda) es el primer bit en row_binary
                # Encontramos el índice correcto de la variable faltante en la representación binaria
                missing_var_index = self.fullSystem.index(missing_var)  # El índice en self.fullSystem de la variable faltante
                #print(row_binary + " -> "+missing_var+" :: "+str(missing_var_index)+" ::: "+row_binary[missing_var_index])
                if row_binary[missing_var_index] == "1":  # Si ese bit es 1, eliminamos la fila
                    should_remove = True
                    break
            
            # Si no hay un "1" en la posición de las variables faltantes, conservar la fila
            if not should_remove:
                #print("--> "+row_binary)
                #print(probabilities[i])
                valid_rows.append(tableCut[i])

        # Imprimir las filas válidas con sus representaciones binarias
        for idx, row in enumerate(valid_rows):
            row_binary = format(idx, f'0{len(self.candidateSystem)}b')
            #print(f'{row_binary}: {row}')
            probabilities_result.append(row)

        #print("-----------------------------------------------")
        return probabilities_result

    def marginalizePresent(self, tableCut, cs):

        cs = cs.upper()
        st.subheader(f"Marginalizando: {cs}")

        # Dimensiones de la tabla original
        row = len(tableCut)
        column = len(tableCut[0])

        # Identificar la variable faltante
        missingVar = set(cs)

        if len(missingVar) != 1:
            raise ValueError("Debe faltar solo una variable en el sistema candidato.")

        # Índice de la variable faltante en full_system
        missing_var_index = self.candidateSystem.index(cs)

        # Crear nueva tabla n x n para almacenar el resultado
        result_table = [[-1] * column for _ in range(int(row/2))]
        rowResult = -1
        
        # Marginalizar la variable faltante
        for rowTraveled in range(row):  # Ahora solo iteramos hasta n

            # Calcular la fila emparejada cambiando solo el bit de la variable faltante
            paired_row = rowTraveled ^ (1 << (len(self.candidateSystem) - missing_var_index - 1))

            # Evitar duplicados, solo multiplicar si paired_row es mayor que col y dentro del rango
            if paired_row > rowTraveled:
                rowResult +=1
                # Multiplicación de columnas y almacenamiento en la nueva tabla
                for col_r in range(column):
                    # Promediamos los valores de las dos columnas marginalizadas
                    result_table[rowResult][col_r] = ((tableCut[rowTraveled][col_r] + tableCut[paired_row][col_r])/2)

        
        return result_table


    def reOrderArray(self, arr):
        # Dimensiones del arreglo original
        n = len(arr)
        m = len(arr[0])

        # Crear el arreglo transpuesto m*n vacío
        arreglo_transpuesto = [[0] * n for _ in range(m)]

        # Recorrer y transponer el arreglo manualmente
        for i in range(n):
            for j in range(m):
                arreglo_transpuesto[j][i] = arr[i][j]

        return arreglo_transpuesto

        # Obtiene la tabla eliminado las filas  que no se encuentre en el parametro de candidateSystem (Cuando el valor binario de la variable es 1)

    def indexCandidateSystem(self):
        
        # Encontrar las variables faltantes
        missing_variables = [var for var in self.fullSystem if var not in self.candidateSystem]
        
        # Tamaño de la matriz
        size = len(self.probabilities)
        num_variables = len(self.fullSystem)
        
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
                missing_var_index = self.fullSystem.index(missing_var)  # El índice en self.fullSystem de la variable faltante
                #print(row_binary + " -> "+missing_var+" :: "+str(missing_var_index)+" ::: "+row_binary[missing_var_index])
                if row_binary[missing_var_index] == "1":  # Si ese bit es 1, eliminamos la fila
                    should_remove = True
                    break
            
            #print(f'{row_binary}: {probabilities[i]}')
            
            # Si no hay un "1" en la posición de las variables faltantes, conservar la fila
            if not should_remove:
                #print("--> "+row_binary)
                #print(probabilities[i])
                valid_rows.append(self.probabilities[i])
        
        # Imprimir las filas válidas con sus representaciones binarias
        for idx, row in enumerate(valid_rows):
            row_binary = format(idx, f'0{len(self.candidateSystem)}b')
            #print(f'{row_binary}: {row}')
            probabilities_result.append(row)

        #print("-----------------------------------------------")
        return probabilities_result

    def marginalize_variableFuture(self):
        # Dimensiones de la tabla original
        n = len(self.probabilities)
        m = len(self.probabilities[0]) if self.probabilities else 0
        
        # Identificar la variable faltante
        missing_var = set(self.fullSystem) - set(self.candidateSystem)
        if len(missing_var) != 1:
            raise ValueError("Debe faltar solo una variable en el sistema candidato.")
        
        missing_var = list(missing_var)[0]
        
        # Índice de la variable faltante en self.fullSystem
        missing_var_index = self.fullSystem.index(missing_var)
        # print(missing_var_index)
        
        # Crear nueva tabla n x n para almacenar el resultado
        result_table = [[0] * n for _ in range(n)]
        
        # Marginalizar la variable faltante
        for col in range(n):  # Ahora solo iteramos hasta n
            # Calcular la columna emparejada cambiando solo el bit de la variable faltante
            paired_row = col ^ (1 << (len(self.fullSystem) - missing_var_index - 1))
            
            # Evitar duplicados, solo multiplicar si paired_row es mayor que col y dentro del rango
            if paired_row > col and paired_row < m:
                # Multiplicación de columnas y almacenamiento en la nueva tabla
                for row in range(n):
                    # Promediamos los valores de las dos columnas marginalizadas
                    result_table[row][col] = (self.probabilities[row][col] + self.probabilities[row][paired_row])
        
        return result_table
    
    def marginalize_variablePresent(self, cs, ns, nsTable):
        
        st.table(nsTable)
        tableCut = self.cut(self.reOrderArray(nsTable))

        st.subheader(f"Cortando - Tabla de estados {ns}'")
        st.table(tableCut)

        tableMarginalized = self.marginalizePresent(tableCut,cs)
        # Siempre en orden de z-a
        #tableMarginalized = self.marginalizePresent(tableCut,"bc")
        st.table(tableMarginalized)

        