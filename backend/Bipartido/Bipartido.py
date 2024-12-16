class Node:
    def __init__(self, value):
        self.value = value
        self.neighbors = []

class Graph:
    def __init__(self):
        self.nodes = []

    def add_node(self, value):
        """Agrega un nodo al grafo."""
        if not any(node.value == value for node in self.nodes):
            self.nodes.append(Node(value))

    def add_edge(self, value1, value2):
        """Crea una arista entre dos nodos."""
        node1 = next((node for node in self.nodes if node.value == value1), None)
        node2 = next((node for node in self.nodes if node.value == value2), None)

        if node1 and node2:
            if node2 not in node1.neighbors:
                node1.neighbors.append(node2)
            if node1 not in node2.neighbors:
                node2.neighbors.append(node1)
        else:
            raise ValueError("Ambos nodos deben existir en el grafo antes de agregar una arista.")

    def remove_edge(self, value1, value2):
        """Elimina la arista entre dos nodos si existe."""
        node1 = next((node for node in self.nodes if node.value == value1), None)
        node2 = next((node for node in self.nodes if node.value == value2), None)

        if node1 and node2:
            if node2 in node1.neighbors:
                node1.neighbors.remove(node2)
            if node1 in node2.neighbors:
                node2.neighbors.remove(node1)

    def is_connected(self):
        """Verifica si el grafo es conexo."""
        if not self.nodes:
            return False

        visited = set()

        def dfs(node):
            visited.add(node)
            for neighbor in node.neighbors:
                if neighbor not in visited:
                    dfs(neighbor)

        # Inicia desde un nodo arbitrario
        dfs(self.nodes[0])

        # Si todos los nodos son visitados, el grafo es conexo
        return len(visited) == len(self.nodes)

    def has_bipartition(self):
        """Verifica si el grafo tiene una bipartición."""
        # Verifica primero si es conexo
        if not self.is_connected():
            return False  # Un grafo no conexo no puede tener bipartición válida

        color = {}

        for node in self.nodes:
            if node not in color:  # Nodo sin visitar
                queue = [node]
                color[node] = 0  # Asigna el primer color
                while queue:
                    current = queue.pop(0)
                    for neighbor in current.neighbors:
                        if neighbor not in color:
                            color[neighbor] = 1 - color[current]  # Colorea opuesto
                            queue.append(neighbor)
                        elif color[neighbor] == color[current]:
                            return False  # Dos nodos conectados tienen el mismo color
        return True