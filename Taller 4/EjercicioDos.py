# =============================================================
# EJERCICIO 2 - ARQUITECTURA SIMP
# Multiplicacion de una matriz 1000x1000 
# Solo se usa Python basico (random, time).
# =============================================================
import random      # para generar numeros aleatorios
import time        # para medir tiempos
import numpy as np
import matplotlib.pyplot as plt

# ---------- PASO 0: parametros ----------
TAMANO_MATRIZ = 1000   # la matriz es de 1000 x 1000
TAMANO_BLOQUE = 100    # cada bloque es de 100 x 100

matrizUno = []
matrizUno = [[random.randint(1, 10) for _ in range(TAMANO_MATRIZ)] for _ in range(TAMANO_MATRIZ)]

matrizDos = []
matrizDos = [[random.randint(1, 10) for _ in range(TAMANO_MATRIZ)] for _ in range(TAMANO_MATRIZ)]

def useNumpy (matrizUno, matrizDos):
        inicio = time.time()   
        m1 = np.array(matrizUno)
        m2 = np.array(matrizDos)
        result = m1 @ m2
        final = time.time() - inicio
        print("Tiempo Numpy : %.4f segundos" % final)
        return result, final

def useSimpleBucle(matrizUno, matrizDos):
    inicio = time.time() 
    matriztres = [[0] * TAMANO_MATRIZ for _ in range(TAMANO_MATRIZ)]
    for i in range(TAMANO_MATRIZ):
        for j in range(TAMANO_MATRIZ):
             for kk in range(TAMANO_MATRIZ):
                matriztres[i][j] += matrizUno[i][kk] * matrizDos[kk][j]
    final = time.time() - inicio
    print("Tiempo Bucle Simple : %.4f segundos" % final)
    return matriztres, final

def printMatriz(matriz):
     for fila in matriz:
        print(fila)

print("Matriz multiplicacion simple:")
_, tiempoBucle = useSimpleBucle(matrizUno, matrizDos)

print("Matriz multiplicacion numpy:")
_, tiempoNumpy = useNumpy(matrizUno, matrizDos)

# ---------- Grafico comparativo de tiempos ----------
etiquetas = ['Bucle Simple', 'NumPy']
tiempos = [tiempoBucle, tiempoNumpy]

barras = plt.bar(etiquetas, tiempos, color=['#3498db', '#2ecc71'])

for barra, tiempo in zip(barras, tiempos):
    plt.text(barra.get_x() + barra.get_width() / 2, barra.get_height(),
              "%.4f s" % tiempo, ha='center', va='bottom')

plt.ylabel("Tiempo de ejecucion (segundos)")
plt.title("Comparacion de tiempos: Bucle Simple vs NumPy")
plt.show()
