# import numpy as np
# from scipy.stats import wasserstein_distance
# from backend.marginalizacion import obtener_tabla_probabilidades
# from backend.auxiliares import repr_current_to_array, repr_next_to_array
# import random

# class ThirdStrategy:
#     def __init__(self, probabilities, cs_value, states, ns, cs, candidate_system, var_data):
#         self.probabilities = probabilities
#         self.cs_value = cs_value
#         self.states = states
#         self.ns = ns
#         self.cs = cs
#         self.candidate_system = candidate_system
#         self.var_data = var_data
#         self.original_system = self._get_original_system()

#     def _get_original_system(self):
#         """
#         Obtiene la tabla de probabilidades del sistema original y la convierte a un array de NumPy.
#         """
#         original_table = obtener_tabla_probabilidades(
#             repr_current_to_array(self.cs, self.cs_value),
#             repr_next_to_array(self.ns),
#             self.probabilities,
#             self.states,
#         )
#         return np.array(original_table).flatten()

#     def _pad_to_same_shape(self, array1, array2):
#         """
#         Asegura que dos arrays tengan la misma forma, rellenando con ceros si es necesario.
#         """
#         max_length = max(array1.shape[0], array2.shape[0])
#         padded_array1 = np.pad(array1, (0, max_length - array1.shape[0]), 'constant')
#         padded_array2 = np.pad(array2, (0, max_length - array2.shape[0]), 'constant')
#         return padded_array1, padded_array2

#     def evaluate_path(self, path):
#         """
#         Evalúa un camino combinando tablas de probabilidades y las convierte a arrays de NumPy.
#         """
#         partitioned_system = np.zeros_like(self.original_system)

#         for (ns_comb, cs_comb) in path:
#             tabla = obtener_tabla_probabilidades(
#                 repr_current_to_array(cs_comb, self.cs_value),
#                 repr_next_to_array(ns_comb),
#                 self.probabilities,
#                 self.states,
#             )
#             tabla_np = np.array(tabla).flatten()

#             # Asegurar que las dimensiones coincidan
#             partitioned_system, tabla_np = self._pad_to_same_shape(partitioned_system, tabla_np)
#             partitioned_system += tabla_np

#         return partitioned_system

#     def calculate_emd(self, partitioned_system):
#         """
#         Calcula la distancia EMD entre el sistema original y el particionado.
#         """
#         # Asegurar que original_system y partitioned_system tienen la misma forma
#         original, partitioned = self._pad_to_same_shape(self.original_system, partitioned_system)
#         return wasserstein_distance(original, partitioned)

#     def run_aco(self, num_ants=20, iterations=50, evaporation=0.5):
#         """
#         Ejecuta la optimización ACO.
#         """
#         pheromones = {state: 1.0 for state in self.ns + self.cs}
#         best_emd = float("inf")
#         best_solution = None

#         for iteration in range(iterations):
#             solutions = []
#             for _ in range(num_ants):
#                 # Generar un camino (combinaciones de ns y cs)
#                 path = []
#                 for _ in range(len(self.ns)):
#                     ns_state = random.choices(self.ns, weights=[pheromones[s] for s in self.ns])[0]
#                     cs_state = random.choices(self.cs, weights=[pheromones[s] for s in self.cs])[0]
#                     path.append((ns_state, cs_state))

#                 # Evaluar el camino
#                 partitioned_system = self.evaluate_path(path)
#                 emd = self.calculate_emd(partitioned_system)
#                 solutions.append((path, emd))

#                 # Actualizar mejor solución
#                 if emd < best_emd:
#                     best_emd = emd
#                     best_solution = path

#             # Actualizar feromonas
#             for (path, emd) in solutions:
#                 for (ns_state, cs_state) in path:
#                     pheromones[ns_state] += 1.0 / (1 + emd)
#                     pheromones[cs_state] += 1.0 / (1 + emd)

#             # Evaporación
#             for state in pheromones:
#                 pheromones[state] *= evaporation

#         return best_solution, best_emd

#     def strategy(self):
#         """
#         Ejecuta la estrategia y muestra resultados.
#         """
#         print("Ejecutando optimización con ACO...")
#         solution, emd = self.run_aco()

#         print("Optimización completada.")
#         print(f"Mejor Partición: {solution}")
#         print(f"EMD Mínimo: {emd}")

#         return solution, emd
import numpy as np
import streamlit as st
from scipy.stats import wasserstein_distance
from backend.marginalizacion import obtener_tabla_probabilidades
from backend.auxiliares import repr_current_to_array, repr_next_to_array
import random

class ThirdStrategy:
    def __init__(self, probabilities, cs_value, states, ns, cs, candidate_system, var_data):
        self.probabilities = probabilities
        self.cs_value = cs_value
        self.states = states
        self.ns = ns
        self.cs = cs
        self.candidate_system = candidate_system
        self.var_data = var_data
        self.original_system = self._get_original_system()
        self.iteration_count = 0

    def _get_original_system(self):
        """
        Obtiene la tabla de probabilidades del sistema original y la convierte a un array de NumPy.
        """
        original_table = obtener_tabla_probabilidades(
            repr_current_to_array(self.cs, self.cs_value),
            repr_next_to_array(self.ns),
            self.probabilities,
            self.states,
        )
        return np.array(original_table).flatten()

    def _pad_to_same_shape(self, array1, array2):
        """
        Asegura que dos arrays tengan la misma forma, rellenando con ceros si es necesario.
        """
        max_length = max(array1.shape[0], array2.shape[0])
        padded_array1 = np.pad(array1, (0, max_length - array1.shape[0]), 'constant')
        padded_array2 = np.pad(array2, (0, max_length - array2.shape[0]), 'constant')
        return padded_array1, padded_array2

    def evaluate_path(self, path):
        """
        Evalúa un camino combinando tablas de probabilidades y las convierte a arrays de NumPy.
        """
        partitioned_system = np.zeros_like(self.original_system)

        for (ns_comb, cs_comb) in path:
            tabla = obtener_tabla_probabilidades(
                repr_current_to_array(cs_comb, self.cs_value),
                repr_next_to_array(ns_comb),
                self.probabilities,
                self.states,
            )
            tabla_np = np.array(tabla).flatten()

            # Asegurar que las dimensiones coincidan
            partitioned_system, tabla_np = self._pad_to_same_shape(partitioned_system, tabla_np)
            partitioned_system += tabla_np

        return partitioned_system

    def format_latex_solution(self, path, emd):
        """
        Formatea una solución como un conjunto LaTeX con conjuntos anidados.
        """
        st.markdown(f"### Mejor Solución de Iteración {self.iteration_count}:")
        latex_parts = []
        for (ns, cs) in path:
            latex_parts.append(rf"\left( \frac{{{ns}}}{{{cs}}} \right)")
        
        # Combinar todas las fracciones con multiplicación entre ellas
        latex_result = " \\times ".join(latex_parts)
        st.latex(rf"""{latex_result}""")
        st.markdown(f"**EMD:** {emd}")

    def run_aco(self, num_ants=20, iterations=10, evaporation=0.5):
        """
        Ejecuta la optimización ACO.
        """
        pheromones = {state: 1.0 for state in self.ns + self.cs}
        best_emd = float("inf")
        best_solution = None

        for iteration in range(1, iterations + 1):
            self.iteration_count = iteration
            solutions = []
            for _ in range(num_ants):
                # Generar un camino (combinaciones de ns y cs)
                path = []
                for _ in range(len(self.ns)):
                    ns_state = random.choices(self.ns, weights=[pheromones[s] for s in self.ns])[0]
                    cs_state = random.choices(self.cs, weights=[pheromones[s] for s in self.cs])[0]
                    path.append((ns_state, cs_state))

                # Evaluar el camino
                partitioned_system = self.evaluate_path(path)
                emd = self.calculate_emd(partitioned_system)
                solutions.append((path, emd))

                # Actualizar mejor solución
                if emd < best_emd:
                    best_emd = emd
                    best_solution = path

            # Mostrar mejores resultados en LaTeX
            if best_solution:
                self.format_latex_solution(best_solution, best_emd)

            # Actualizar feromonas
            for (path, emd) in solutions:
                for (ns_state, cs_state) in path:
                    pheromones[ns_state] += 1.0 / (1 + emd)
                    pheromones[cs_state] += 1.0 / (1 + emd)

            # Evaporación
            for state in pheromones:
                pheromones[state] *= evaporation

        return best_solution, best_emd

    def calculate_emd(self, partitioned_system):
        """
        Calcula la distancia EMD entre el sistema original y el particionado.
        """
        original, partitioned = self._pad_to_same_shape(self.original_system, partitioned_system)
        return wasserstein_distance(original, partitioned)

    def strategy(self):
        """
        Ejecuta la estrategia y muestra resultados.
        """
        st.header("Ejecución de Optimización con ACO")
        solution, emd = self.run_aco()

        st.success("Optimización completada.")
        st.subheader("Mejor Resultado Global:")
        if solution:
            self.format_latex_solution(solution, emd)
        return solution, emd
