
# Algoritmo de Bellman-Ford

def bellman_ford(graph, source):
    # Inicialización: distancias a todos los nodos son infinitas, excepto al nodo fuente.
    distances = {node: float('inf') for node in graph}
    distances[source] = 0

    # Relajación de las aristas (V-1) veces, donde V es el número de vértices
    for _ in range(len(graph) - 1):
        for u in graph:
            for v, weight in graph[u]:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight

    # Verificación de ciclos negativos: si se puede mejorar una distancia, hay un ciclo negativo
    for u in graph:
        
        for v, weight in graph[u]:
            if distances[u] + weight < distances[v]:
                print("El grafo contiene un ciclo negativo.")
                return None  # Si hay ciclo negativo, retornamos None.

    return distances

# Ejemplo de grafo:
# El grafo se representa como un diccionario de listas de adyacencia.
# Cada nodo tiene una lista de tuplas (vecino, peso).
graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('C', -2), ('D', 2)],
    'C': [('D', 3)],
    'D': []
}

# Usamos el nodo 'A' como fuente
source = 'A'
distances = bellman_ford(graph, source)

if distances:
    print(f"Distancias más cortas desde el nodo fuente '{source}':")
    for node, dist in distances.items():
        print(f"{node}: {dist}")
