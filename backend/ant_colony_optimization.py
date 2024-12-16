import itertools
import random
import numpy as np
from scipy.stats import wasserstein_distance

class AntColonyOptimization:
    def __init__(self, original_system, probabilities, states, ns, cs, num_ants=10, iterations=50, alpha=1, beta=2, rho=0.5):
        self.original_system = np.array(original_system, dtype=float)
        self.probabilities = probabilities
        self.states = states
        self.ns = ns
        self.cs = cs
        self.num_ants = num_ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.pheromones = {}  # Diccionario para almacenar las feromonas
        self.best_solution = None
        self.min_emd = float("inf")

    def evaluate_path(self, path):
        """
        Evalúa un camino generado por las hormigas y devuelve el sistema particionado.
        """
        partitioned_system = []
        for partition in path:
            ns_comb, cs_comb = partition
            # Convierte las combinaciones a valores numéricos si es necesario
            ns_sum = sum([ord(char) - ord('A') + 1 for char in ns_comb])
            cs_sum = sum([ord(char) - ord('A') + 1 for char in cs_comb])
            partitioned_value = ns_sum + cs_sum
            partitioned_system.append(partitioned_value)
        return np.array(partitioned_system, dtype=float)

    def initialize_pheromones(self):
        # Inicializar con valores pequeños para todas las combinaciones posibles
        for ns_comb in itertools.permutations(self.ns):
            for cs_comb in itertools.permutations(self.cs):
                self.pheromones[(ns_comb, cs_comb)] = 0.1

    def calculate_emd(self, partitioned_system):
        """
        Calcular la distancia EMD entre el sistema original y la partición.
        """
        try:
            partitioned_system = np.array(partitioned_system, dtype=float)
            return wasserstein_distance(self.original_system, partitioned_system)
        except ValueError as e:
            raise ValueError(f"Error al calcular EMD: {e}\nPartitioned System: {partitioned_system}")

    def get_neighbors(self, current_partition):
        """
        Retorna los vecinos del estado actual (partición actual).
        En este caso, las combinaciones válidas de 'ns' y 'cs' que no han sido visitadas.
        """
        neighbors = []
        if current_partition is None:
            neighbors = [(ns_comb, cs_comb) for ns_comb in itertools.permutations(self.ns)
                                            for cs_comb in itertools.permutations(self.cs)]
        else:
            current_ns, current_cs = current_partition
            for ns_comb in itertools.permutations(self.ns):
                for cs_comb in itertools.permutations(self.cs):
                    if (ns_comb, cs_comb) != current_partition:
                        neighbors.append((ns_comb, cs_comb))
        return neighbors

    def select_next(self, current_partition):
        neighbors = self.get_neighbors(current_partition)
        if not neighbors:
            return None  # No hay vecinos disponibles

        probabilities = []
        for neighbor in neighbors:
            pheromone = self.pheromones.get(neighbor, 0.1)
            heuristic = 1 / (self.calculate_emd(neighbor) + 1e-10)  # Heurística inversa del EMD
            probabilities.append(pheromone ** self.alpha * heuristic ** self.beta)

        probabilities = np.array(probabilities, dtype=float)
        if np.sum(probabilities) == 0:
            probabilities = np.ones(len(probabilities)) / len(probabilities)
        else:
            probabilities /= np.sum(probabilities)  # Normalización

        return neighbors[np.random.choice(len(neighbors), p=probabilities)]

    def update_pheromones(self, paths):
        # Actualización de las feromonas basadas en las soluciones encontradas
        for key in self.pheromones:
            self.pheromones[key] *= (1 - self.rho)  # Evaporación
        for path, emd in paths:
            for i in range(len(path) - 1):
                self.pheromones[(path[i], path[i + 1])] += 1 / (emd + 1e-10)

    def run(self):
        self.initialize_pheromones()
        for _ in range(self.iterations):
            paths = []
            for _ in range(self.num_ants):
                path = [random.choice(list(self.pheromones.keys()))]  # Selección inicial
                while len(path) < len(self.ns) + len(self.cs):
                    next_partition = self.select_next(path[-1])
                    if next_partition is None:
                        break
                    path.append(next_partition)

                # Calcular EMD para la partición
                partitioned_system = self.evaluate_path(path)
                emd = self.calculate_emd(partitioned_system)
                paths.append((path, emd))

                # Actualizar la mejor solución
                if emd < self.min_emd:
                    self.min_emd = emd
                    self.best_solution = path

            self.update_pheromones(paths)

        return self.best_solution, self.min_emd
