import random
import threading
import time
import numpy as np
import matplotlib.pyplot as plt


TAMANO_MATRIZ = 10000   # la matriz es de 10000 x 10000
TAMANO_BLOQUE = 1000    # cada bloque es de 1000 x 1000
BLOQUES_POR_LADO = TAMANO_MATRIZ // TAMANO_BLOQUE   # 10000/1000 = 100
TOTAL_BLOQUES = BLOQUES_POR_LADO * BLOQUES_POR_LADO # 100*100 = 1000 bloques

print("Creando matriz ...")

matriz = np.random.randint(1, 1000, size=(TAMANO_MATRIZ, TAMANO_MATRIZ))

print("Dividiendo la matriz en", TOTAL_BLOQUES, "bloques de 1000x1000 ...")
bloques = []
for bi in range(BLOQUES_POR_LADO):
    for bj in range(BLOQUES_POR_LADO):
        fila_inicio = bi * TAMANO_BLOQUE
        col_inicio = bj * TAMANO_BLOQUE
        # El slicing crea una vista del bloque (no copia datos)
        bloque = matriz[fila_inicio:fila_inicio + TAMANO_BLOQUE,
                        col_inicio:col_inicio + TAMANO_BLOQUE]
        bloques.append(bloque)
        


# ---------- Funcion que suma UN bloque ----------
def sumar_bloque(bloque):
    sumas_de_columnas = bloque.sum(axis=0)   # vector de 1000 sumas
    return int(sumas_de_columnas.sum())

# ---------- VERSION SECUENCIAL  ----------

print("Caluclando secuencia ...")

inicio = time.time()                       
suma_secuencial = 0.0
for bloque in bloques:
    suma_secuencial = suma_secuencial + sumar_bloque(bloque)
tiempo_secuencial = time.time() - inicio   


print("Caluclando hibrido ...")
# ---------- VERSION HIBRIDA SMP + SIMD  ----------
resultados = [0] * TOTAL_BLOQUES

def tarea_del_hilo(indice):
    """Lo que ejecuta cada hilo: suma su bloque y guarda el resultado."""
    resultados[indice] = sumar_bloque(bloques[indice])

inicio = time.time()



hilos = []
for k in range(TOTAL_BLOQUES):
    hilo = threading.Thread(target=tarea_del_hilo, args=(k,))
    hilos.append(hilo)

# Lanzar todos los hilos
for hilo in hilos:
    hilo.start()

# Esperar a que TODOS terminen (join)
for hilo in hilos:
    hilo.join()


suma_paralela = 0.0
for parcial in resultados:
    suma_paralela = suma_paralela + parcial

tiempo_hibrido = time.time() - inicio


# ---------- RESULTADOS ----------
print("\n================ RESULTADOS ================")

print("Tiempo SECUENCIAL: %.4f segundos" % tiempo_secuencial)
print("Tiempo HIBRIDO  : %.4f segundos" % tiempo_hibrido)

if tiempo_hibrido < tiempo_secuencial:
    print("El metodo HIBRIDO es mas rapido por :",
          (tiempo_secuencial - tiempo_hibrido))
else:
    print("El metodo SECUENCIAL es mas rapido por :",
          (tiempo_hibrido - tiempo_secuencial))

# ---------- Grafico comparativo de tiempos ----------
etiquetas = ['Secuencial', 'Hibrido']
tiempos = [tiempo_secuencial, tiempo_hibrido]

barras = plt.bar(etiquetas, tiempos, color=['#3498db', '#2ecc71'])

for barra, tiempo in zip(barras, tiempos):
    plt.text(barra.get_x() + barra.get_width() / 2, barra.get_height(),
              "%.4f s" % tiempo, ha='center', va='bottom')

plt.ylabel("Tiempo de ejecucion (segundos)")
plt.title("Comparacion de tiempos: Secuencial vs Hibrido")
plt.show()