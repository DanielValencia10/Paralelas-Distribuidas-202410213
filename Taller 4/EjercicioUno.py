import random
import threading
import time
import numpy as np
import matplotlib.pyplot as plt


TAMANO_MATRIZ = 1000   # la matriz es de 1000 x 1000
TAMANO_BLOQUE = 100    # cada bloque es de 100 x 100
BLOQUES_POR_LADO = TAMANO_MATRIZ // TAMANO_BLOQUE   # 1000/100 = 10
TOTAL_BLOQUES = BLOQUES_POR_LADO * BLOQUES_POR_LADO # 10*10 = 100 bloques

print("Creando matriz ...")
matriz= [[random.randint(1, 1000) for _ in range(TAMANO_MATRIZ)] for _ in range(TAMANO_MATRIZ)]


print("Dividiendo la matriz en", TOTAL_BLOQUES, "bloques de 100x100 ...")
bloques = []
for bi in range(BLOQUES_POR_LADO):
    for bj in range(BLOQUES_POR_LADO):
        bloque = []
        fila_inicio = bi * TAMANO_BLOQUE
        col_inicio = bj * TAMANO_BLOQUE
        for i in range(fila_inicio, fila_inicio + TAMANO_BLOQUE):
            fila_del_bloque = []
            for j in range(col_inicio, col_inicio + TAMANO_BLOQUE):
                fila_del_bloque.append(matriz[i][j])
            bloque.append(fila_del_bloque)
        bloques.append(bloque)



# ---------- Funcion que suma UN bloque ----------
def sumar_bloque(bloque):
    """Recorre todos los elementos del bloque y los suma."""
    suma = 0.0
    for fila in bloque:
        for elemento in fila:
            suma = suma + elemento
    return suma

# ---------- VERSION SECUENCIAL  ----------

print("Caluclando secuencia ...")

inicio = time.time()                       
suma_secuencial = 0.0
for bloque in bloques:
    suma_secuencial = suma_secuencial + sumar_bloque(bloque)
tiempo_secuencial = time.time() - inicio   


print("Caluclando paralela ...")
# ---------- VERSION PARALELA  ----------
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

tiempo_paralelo = time.time() - inicio


# ---------- RESULTADOS ----------
print("\n================ RESULTADOS ================")

print("Tiempo secuencial: %.4f segundos" % tiempo_secuencial)
print("Tiempo paralelo  : %.4f segundos" % tiempo_paralelo)
if (tiempo_paralelo> tiempo_secuencial):
    print ("El metodo paralelo es más rapido por:" , (tiempo_paralelo - tiempo_secuencial))

else:
    print ("El metodo secuencial es más rapido por: ",  (tiempo_secuencial - tiempo_paralelo) )

# ---------- Grafico comparativo de tiempos ----------
etiquetas = ['Secuencial', 'Paralelo']
tiempos = [tiempo_secuencial, tiempo_paralelo]

barras = plt.bar(etiquetas, tiempos, color=['#3498db', '#2ecc71'])

for barra, tiempo in zip(barras, tiempos):
    plt.text(barra.get_x() + barra.get_width() / 2, barra.get_height(),
              "%.4f s" % tiempo, ha='center', va='bottom')

plt.ylabel("Tiempo de ejecucion (segundos)")
plt.title("Comparacion de tiempos: Secuencial vs Paralelo")
plt.show()
