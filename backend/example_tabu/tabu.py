import random

def objective_function(solution):
    return sum(solution)

def get_neighbors(solution):
    neighbors = []
    for i in range(len(solution)):
        for j in range(i + 1, len(solution)):
            neighbor = solution[:]
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            neighbors.append(neighbor)
    return neighbors

def tabu_search(initial_solution, max_iterations, tabu_list_size):
    best_solution = initial_solution
    current_solution = initial_solution
    tabu_list = []

    for _ in range(max_iterations):
        neighbors = get_neighbors(current_solution)
        best_neighbor = None
        best_neighbor_fitness = float('inf')

        for neighbor in neighbors:
            if neighbor not in tabu_list:
                neighbor_fitness = objective_function(neighbor)
                if neighbor_fitness < best_neighbor_fitness:  # Correct comparison
                    best_neighbor = neighbor
                    best_neighbor_fitness = neighbor_fitness

        if best_neighbor is None:
            break

        current_solution = best_neighbor
        tabu_list.append(best_neighbor)
        if len(tabu_list) > tabu_list_size:  # Correct comparison
            tabu_list.pop(0)

        if objective_function(best_neighbor) < objective_function(best_solution):
            best_solution = best_neighbor

    return best_solution


# Example usage
initial_solution = [1, 2, 3, 4, 5]
max_iterations = 100
tabu_list_size = 10

best_solution = tabu_search(initial_solution, max_iterations, tabu_list_size)
print("Best solution: {}".format(best_solution))
print("Best solution fitness: {}".format(objective_function(best_solution)))
