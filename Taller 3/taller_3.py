import random
import threading
import time

BOLETAS = 50          # boletas disponibles
COMPRADORES = 100     # hilos que intentan comprar
TIEMPO_PAGO = 0.01    # segundos que tarda validar un pago
PAGOS_SIMULTANEOS = 5 # capacidad de la pasarela de pago

# variables globales (compartidas)
disponibles = BOLETAS
vendidas = 0
lock = threading.Lock()
pasarela = threading.Semaphore(PAGOS_SIMULTANEOS)
inicio_venta = threading.Event()   # "señal de arranque": todos compran a la vez


def procesar_pago(rng, prob_fallo):
    """Simula la validación del pago. Devuelve True si el pago fue aprobado."""
    time.sleep(TIEMPO_PAGO)
    return rng.random() >= prob_fallo


# V1: SIN LOCK  (race condition: verificar y descontar no es atómico)
def comprar_v1(i, resultados, rng):
    global disponibles, vendidas
    inicio_venta.wait()
    if disponibles > 0:                 # verifica
        procesar_pago(rng, 0)           # paga (otros hilos ven "disponibles > 0")
        disponibles -= 1                # descuenta
        vendidas += 1
        resultados[i] = "COMPRO"
    else:
        resultados[i] = "AGOTADO"


# V2: LOCK con el pago DENTRO (correcto, pero serializa todo)
def comprar_v2(i, resultados, rng):
    global disponibles, vendidas
    inicio_venta.wait()
    with lock:
        if disponibles > 0:
            procesar_pago(rng, 0)       # el pago bloquea a todos los demás
            disponibles -= 1
            vendidas += 1
            resultados[i] = "COMPRO"
        else:
            resultados[i] = "AGOTADO"


# V3: LOCK MÍNIMO + SEMAPHORE (reserva dentro, pago fuera)
def crear_comprar_v3(prob_fallo):
    def comprar_v3(i, resultados, rng):
        global disponibles, vendidas
        inicio_venta.wait()

        with lock:                      # sección crítica mínima: solo reservar
            if disponibles == 0:
                resultados[i] = "AGOTADO"
                return
            disponibles -= 1            # reserva la boleta

        with pasarela:                  # Semaphore(5): máx. 5 pagos a la vez
            aprobado = procesar_pago(rng, prob_fallo)

        with lock:                      # confirmar o devolver la boleta
            if aprobado:
                vendidas += 1
                resultados[i] = "COMPRO"
            else:
                disponibles += 1        # el pago falló: se libera la boleta
                resultados[i] = "PAGO FALLIDO"
    return comprar_v3


# Ejecutor
def ejecutar(nombre, funcion, semilla):
    global disponibles, vendidas
    disponibles, vendidas = BOLETAS, 0
    inicio_venta.clear()

    resultados = [None] * COMPRADORES
    hilos = [
        threading.Thread(
            target=funcion,
            # cada hilo con su propio generador aleatorio (reproducible)
            args=(i, resultados, random.Random(semilla + i)),
        )
        for i in range(COMPRADORES)
    ]
    for h in hilos:
        h.start()

    t0 = time.perf_counter()
    inicio_venta.set()                  # ¡se abre la venta!
    for h in hilos:
        h.join()
    t = time.perf_counter() - t0

    correcto = (vendidas <= BOLETAS and disponibles >= 0
                and vendidas + disponibles == BOLETAS)
    estado = "CORRECTO" if correcto else "ERROR (sobreventa)"
    sin_vender = disponibles if correcto else 0
    print(f"{nombre:<26} vendidas: {vendidas:3d} | disponibles: {disponibles:3d} "
          f"| tiempo: {t:6.3f}s | {estado}"
          + (f" | boletas sin vender: {sin_vender}" if sin_vender else ""))
    return correcto, t


if __name__ == "__main__":
    print(f"{BOLETAS} boletas, {COMPRADORES} compradores, "
          f"pago = {TIEMPO_PAGO}s, pasarela = {PAGOS_SIMULTANEOS} simultáneos\n")

    for corrida in range(1, 4):
        print(f"--- Corrida {corrida} ---")
        s = corrida * 1000
        ejecutar("comprar_v1  sin lock", comprar_v1, s)
        ejecutar("comprar_v2  lock (pago dentro)", comprar_v2, s)
        ejecutar("comprar_v3  lock mínimo+semáforo", crear_comprar_v3(0.0), s)
        ejecutar("comprar_v3b con 20% pagos fallidos", crear_comprar_v3(0.20), s)
        print()
