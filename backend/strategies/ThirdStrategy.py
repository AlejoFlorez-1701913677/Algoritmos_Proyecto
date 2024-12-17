import numpy as np
import time
from datetime import datetime
import streamlit as st
from scipy.stats import wasserstein_distance
import random
from backend.marginalizacion import obtener_tabla_probabilidades
from backend.auxiliares import repr_current_to_array, repr_next_to_array, ordenar_matriz_product


class ThirdStrategy:
    def __init__(self, probabilities, cs_value, states, ns, cs):
        """
        Inicializa la estrategia ACO.
        """
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.states = states
        self.ns = ns
        self.cs = cs
        self.original_system = self._get_original_system()
        self.best_partition = None
        self.best_emd = float("inf")
        self.all_solutions = []

    def _get_original_system(self):
        """
        Obtiene la tabla de probabilidades del sistema original.
        """
        original_table = obtener_tabla_probabilidades(
            repr_current_to_array(self.cs, self.cs_value),
            repr_next_to_array(self.ns),
            self.probabilities,
            self.states
        )
        return np.array(original_table).flatten()

    def _pad_to_same_shape(self, array1, array2):
        """
        Asegura que dos arrays tengan la misma forma.
        """
        max_length = max(array1.shape[0], array2.shape[0])
        padded_array1 = np.pad(array1, (0, max_length - array1.shape[0]), 'constant')
        padded_array2 = np.pad(array2, (0, max_length - array2.shape[0]), 'constant')
        return padded_array1, padded_array2

    def evaluate_partition(self, partition):
        """
        Evalúa una partición calculando su sistema y la distancia EMD.
        """
        partitioned_system = np.zeros_like(self.original_system)

        for subset_ns, subset_cs in partition:
            tabla = obtener_tabla_probabilidades(
                repr_current_to_array(subset_cs, self.cs_value),
                repr_next_to_array(subset_ns),
                self.probabilities,
                self.states
            )
            tabla_np = np.array(tabla).flatten()
            partitioned_system, tabla_np = self._pad_to_same_shape(partitioned_system, tabla_np)
            partitioned_system += tabla_np

        # Calcula el EMD
        original, partitioned = self._pad_to_same_shape(self.original_system, partitioned_system)
        emd = wasserstein_distance(original, partitioned)

        return emd

    def generate_valid_partitions(self):
        """
        Genera particiones válidas de ns y cs asegurando que no haya repetidos entre los conjuntos.
        """
        partitions = []
        ns_set = set(self.ns)
        cs_set = set(self.cs)

        for i in range(1, len(self.ns)+1):
            left_ns = list(self.ns[:i])
            right_ns = list(ns_set - set(left_ns))

            left_cs = list(self.cs[:i])
            right_cs = list(cs_set - set(left_cs))

            if set(left_ns).isdisjoint(right_ns) and set(left_cs).isdisjoint(right_cs):
                partitions.append(((tuple(left_ns), tuple(left_cs)), (tuple(right_ns), tuple(right_cs))))  # Convertir a tupla
        return partitions

    # def run_aco(self, num_ants=20, iterations=50, evaporation=0.5, alpha=1.0, beta=2.0):
    #     """
    #     Ejecuta la optimización ACO para encontrar la mejor partición.
    #     """
    #     st.header("Ejecución de Tercera Estrategia con ACO")
    #     valid_partitions = self.generate_valid_partitions()  # Genera particiones válidas
    #     pheromones = {str(p): 2.0 for p in valid_partitions}  # Feromonas iniciales
    #     best_solution = None
    #     best_quality = -np.inf  # Suponiendo que estamos maximizando alguna calidad

    #     for iteration in range(iterations):
    #         st.subheader(f"Iteración {iteration + 1}")
    #         solutions = []

    #         # Cada hormiga construye una solución
    #         for _ in range(num_ants):
    #             path = []
    #             total_quality = 0

    #             # Selecciona 2 subconjuntos válidos
    #             for _ in range(2):  # Asumiendo que seleccionas 2 particiones
    #                 # Calcular las probabilidades de selección con la fórmula ACO
    #                 probabilities = []
    #                 for partition in valid_partitions:
    #                     pheromone_strength = pheromones[str(partition)] ** alpha
    #                     visibility = self.evaluate_partition(partition) ** beta  # Suponiendo que hay una función para evaluar la calidad de la partición
    #                     probabilities.append(pheromone_strength * visibility)

    #                 # Normalizar las probabilidades
    #                 total_pheromone = sum(probabilities)
    #                 probabilities = [p / total_pheromone for p in probabilities]

    #                 # Selección probabilística
    #                 selected_partition = random.choices(valid_partitions, weights=probabilities, k=1)[0]
    #                 path.append(selected_partition)
    #                 total_quality += self.evaluate_partition(selected_partition)  # Acumula la calidad

    #             # Al final de la construcción de la solución por la hormiga
    #             solutions.append((path, total_quality))

    #             # Actualizar la mejor solución si es necesario
    #             if total_quality > best_quality:
    #                 best_solution = path
    #                 best_quality = total_quality

    #         # Evaporación de feromonas
    #         for partition in pheromones:
    #             pheromones[partition] *= (1 - evaporation)

    #         # Actualización de feromonas por las soluciones encontradas
    #         for path, quality in solutions:
    #             for partition in path:
    #                 pheromones[str(partition)] += quality

    #         st.write(f"Mejor solución en esta iteración: {best_solution} con calidad {best_quality}")

    #     st.write(f"Mejor solución final: {best_solution} con calidad {best_quality}")

    #     return best_solution,best_quality

    def run_aco(self, num_ants=20, iterations=5, evaporation=0.5, alpha=1.0, beta=2.0):
         """
         Ejecuta la optimización ACO para encontrar la mejor partición.
         """
         start_time = time.time()

        # Convertir a un objeto datetime
         dt_object = datetime.fromtimestamp(start_time)

        # Formatear como cadena de fecha y hora
         formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')
         #st.header("Ejecución de Tercera Estrategia con ACO")
         valid_partitions = self.generate_valid_partitions()
         pheromones = {str(p): 2.0 for p in valid_partitions}  # Convertir a string para clave del diccionario

         for iteration in range(iterations):
             #st.subheader(f"Iteración {iteration + 1}")
             solutions = []

             for _ in range(num_ants):
                 path = []
                 for _ in range(2):  # Selecciona 2 subconjuntos válidos
                     probabilities = [pheromones[str(p)] ** alpha for p in valid_partitions]
                     probabilities /= np.sum(probabilities)
                     #st.text(f'{valid_partitions}')
                     selected_partition = random.choices(
                         list(valid_partitions), weights=probabilities, k=1
                     )[0]
                     path.append(selected_partition)

                 # Evaluar la solución
                 emd = self.evaluate_partition(path)
                 solutions.append((path, emd))
                 #st.text(f'{emd}')
                 # Actualizar mejor solución
                 if emd < self.best_emd:
                     self.best_emd = emd
                     self.best_partition = path
             # Actualizar feromonas
             for partition_str in pheromones:
                 pheromones[partition_str] *= (1 - evaporation)  # Evaporación
             for path, emd in solutions:
                 for partition in path:
                     pheromones[str(partition)] += 1.0 / (1 + emd)  # Incremento por calidad
             #st.text(f'{path}')

         if self.best_partition:
            left, right = self.best_partition

            # Asegurarnos de convertir las tuplas en cadenas
            ns_left = "".join(map(str, left[0][1]))  # Convertir elementos en left[0] a cadena
            cs_left = "".join(map(str, left[1][1]))  # Convertir elementos en left[1] a cadena
            ns_right = "".join(map(str, right[0][0]))  # Convertir elementos en right[0] a cadena
            cs_right = "".join(map(str, right[1][0]))
        
         end_time = time.time()

         # Convertir a un objeto datetime
         dt_objectEnd = datetime.fromtimestamp(end_time)
         # Formatear como cadena de fecha y hora
         formatted_time_end = dt_objectEnd.strftime('%Y-%m-%d %H:%M:%S.%f')

         elapsed_time = end_time - start_time

        # Convertir a un objeto datetime
         dt_object_elapsed_time = datetime.fromtimestamp(elapsed_time)
        # Formatear como cadena de fecha y hora
         formatted_time_elapsed_time = dt_object_elapsed_time.strftime('%M:%S.%f')

         return [(ns_right,cs_left),(cs_right,ns_left)], self.best_emd,formatted_time_elapsed_time

    def _show_results(self):
        """
        Muestra todas las soluciones evaluadas y la mejor partición.
        """
        st.subheader("Mejor Resultado Global:")
        if self.best_partition:
            left, right = self.best_partition

            # Asegurarnos de convertir las tuplas en cadenas
            ns_left = "".join(map(str, left[0][1]))  # Convertir elementos en left[0] a cadena
            cs_left = "".join(map(str, left[1][1]))  # Convertir elementos en left[1] a cadena
            ns_right = "".join(map(str, right[0][0]))  # Convertir elementos en right[0] a cadena
            cs_right = "".join(map(str, right[1][0]))  # Convertir elementos en right[1] a cadena

            # Formato de LaTeX
            latex_result = (
                rf"\left( \frac{{{ns_left}}}{{{cs_right}}} \right)"
                rf" \times \left( \frac{{{cs_left}}}{{{ns_right}}} \right)"
            )
            st.latex(latex_result)
            st.write(f"**EMD Mínimo:** {self.best_emd}")
