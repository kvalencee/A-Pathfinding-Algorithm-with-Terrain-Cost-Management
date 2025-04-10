import heapq
from collections import defaultdict


def a_estrella(problema):
    frontera = []
    heapq.heappush(frontera, (0, 0, problema.estado_inicial))

    came_from = {}
    g_score = {problema.estado_inicial: 0}
    f_score = {problema.estado_inicial: problema.heuristica(problema.estado_inicial)}

    open_set = {problema.estado_inicial}
    closed_set = set()
    orden_exploracion = []
    arbol_busqueda = defaultdict(list)
    contador = 1  # Para mantener un orden consistente en el heap

    while frontera:
        _, _, current = heapq.heappop(frontera)

        if current not in open_set:
            continue

        if problema.es_objetivo(current):
            # Reconstruir camino
            camino = []
            while current in came_from:
                camino.append(current)
                current = came_from[current]
            camino.append(problema.estado_inicial)
            camino.reverse()

            # Calcular costo total correctamente
            costo_total = sum(
                problema.agente.costo_movimiento(problema.laberinto[e.fila][e.columna])
                for e in camino[1:]
            )
            problema.costo_acumulado = costo_total

            return camino, open_set, closed_set, orden_exploracion, arbol_busqueda

        open_set.remove(current)
        closed_set.add(current)
        orden_exploracion.append(('cerrado', current))

        for accion, neighbor in problema.obtener_acciones(current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + accion.costo

            if neighbor not in open_set:
                open_set.add(neighbor)
                orden_exploracion.append(('abierto', neighbor))
                arbol_busqueda[current].append(neighbor)
                heapq.heappush(frontera, (tentative_g + problema.heuristica(neighbor), contador, neighbor))
                contador += 1
            elif tentative_g >= g_score.get(neighbor, float('inf')):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            f_score[neighbor] = tentative_g + problema.heuristica(neighbor)

    return None, open_set, closed_set, orden_exploracion, arbol_busqueda