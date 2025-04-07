import heapq
from collections import defaultdict


def a_estrella(problema):
    frontera = []
    # Usamos un contador para evitar comparar Estados directamente
    contador = 0
    heapq.heappush(frontera, (0, contador, problema.estado_inicial))
    contador += 1

    came_from = {}
    costo_acumulado = defaultdict(lambda: float('inf'))
    costo_acumulado[problema.estado_inicial] = 0

    costo_estimado = defaultdict(lambda: float('inf'))
    costo_estimado[problema.estado_inicial] = problema.heuristica(problema.estado_inicial)

    while frontera:
        _, _, estado_actual = heapq.heappop(frontera)

        if problema.es_objetivo(estado_actual):
            camino = []
            while estado_actual in came_from:
                camino.append(estado_actual)
                estado_actual = came_from[estado_actual]
            camino.append(problema.estado_inicial)
            camino.reverse()
            return camino

        for accion, estado_siguiente in problema.obtener_acciones(estado_actual):
            nuevo_costo = costo_acumulado[estado_actual] + accion.costo

            if nuevo_costo < costo_acumulado[estado_siguiente]:
                came_from[estado_siguiente] = estado_actual
                costo_acumulado[estado_siguiente] = nuevo_costo
                estimado = nuevo_costo + problema.heuristica(estado_siguiente)
                heapq.heappush(frontera, (estimado, contador, estado_siguiente))
                contador += 1
                costo_estimado[estado_siguiente] = estimado

    return None