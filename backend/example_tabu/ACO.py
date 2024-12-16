import random
import numpy as np
import matplotlib.pyplot as plt

# Función para generar la matriz con números aleatorios
def generar_matriz(n, m):
    matriz = []
    for i in range(n):
        fila = [round(random.uniform(0, 1), 2) for _ in range(m)]  # Redondear a 2 decimales
        matriz.append(fila)
    return matriz

# Parámetros del ACO
n = 4  # Número de filas (puntos/nodos)
m = 4  # Número de columnas (dimensiones)

# Definir la matriz de distancias
matriz = generar_matriz(n, m)

# Número de hormigas
num_hormigas = 10
# Número de iteraciones
num_iteraciones = 100
# Parámetros del ACO
evaporacion = 0.5  # Factor de evaporación
peso_feromona = 1.0  # Peso de la feromona
peso_distancia = 1.0  # Peso de la distancia en la probabilidad

# Inicializar feromonas en todas las rutas (matriz de feromonas)
feromonas = np.ones((n, m)) * 0.1  # Feromonas iniciales

# Función de probabilidad para elegir la siguiente ciudad
def probabilidad_traslado(actual, siguiente):
    denominador = 0
    for j in range(m):
        if actual != j:  # Asegurarse de que no sea el mismo nodo
            denominador += (feromonas[actual][j] ** peso_feromona) * ((1 / matriz[actual][j]) ** peso_distancia)
    
    numerador = (feromonas[actual][siguiente] ** peso_feromona) * ((1 / matriz[actual][siguiente]) ** peso_distancia)
    
    # Si el denominador es 0, se asigna una probabilidad igual para todas las opciones
    if denominador == 0:
        return 1 / n  # Probabilidad uniforme si todas las probabilidades son iguales
    return numerador / denominador

# Función de ACO
def aco():
    global feromonas  # Asegurarse de que se usa la variable global
    mejores_rutas = []
    mejor_costo = float('inf')
    
    for _ in range(num_iteraciones):
        # Crear una lista para almacenar las rutas de las hormigas
        rutas_hormigas = []
        
        # Para cada hormiga
        for _ in range(num_hormigas):
            ruta = []
            actual = 0  # Comenzar desde el nodo 0 (puedes ajustar este valor)
            visitados = [False] * n  # Lista de nodos visitados
            visitados[actual] = True  # Marcar el nodo inicial como visitado
            ruta.append(actual)
            
            # Construir la ruta de la hormiga
            while len(ruta) < n:
                probabilidades = [probabilidad_traslado(actual, siguiente) for siguiente in range(n) if not visitados[siguiente]]
                if sum(probabilidades) == 0:  # Evitar la suma cero
                    probabilidades = [1 / n] * (n - len(ruta))  # Probabilidad uniforme en caso de no haber opciones
                siguiente = np.random.choice([i for i in range(n) if not visitados[i]], p=probabilidades)  # Elegir siguiente nodo
                ruta.append(siguiente)
                visitados[siguiente] = True
                actual = siguiente
            
            # Calcular el costo de la ruta
            costo = sum(matriz[ruta[i]][ruta[i+1]] for i in range(len(ruta) - 1))  # Ajusta la fórmula de acuerdo a tu problema
            
            # Actualizar la mejor ruta y costo
            if costo < mejor_costo:
                mejor_costo = costo
                mejores_rutas = ruta
        
        # Actualizar las feromonas
        feromonas = feromonas * (1 - evaporacion)  # Evaporación de feromonas
        for ruta in mejores_rutas:
            for i in range(len(ruta) - 1):
                feromonas[ruta[i]][ruta[i+1]] += 1 / mejor_costo  # Actualizar feromonas basadas en el costo de la mejor ruta
    
    return mejores_rutas, mejor_costo

# Ejecutar el ACO
mejores_rutas, mejor_costo = aco()
print("Mejor ruta:", mejores_rutas)
print("Mejor costo:", mejor_costo)
