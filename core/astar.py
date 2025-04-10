import heapq
from collections import defaultdict


def a_estrella_corregido(problema):
    frontera = []
    # Inicializar con (f_score, contador, estado_inicial)
    heapq.heappush(frontera, (problema.heuristica(problema.estado_inicial), 0, problema.estado_inicial))

    came_from = {}  # Para reconstruir el camino
    g_score = {problema.estado_inicial: 0}  # Costo real desde el inicio hasta cada nodo

    en_frontera = {problema.estado_inicial}
    closed_set = set()
    orden_exploracion = []
    orden_exploracion.append(('abierto', problema.estado_inicial))  # Añadir estado inicial como abierto
    arbol_busqueda = defaultdict(list)
    contador = 1  # Para mantener orden en el heap cuando hay empates

    while frontera:
        f_actual, _, current = heapq.heappop(frontera)

        # Si ya no está en la frontera (puede haber duplicados en el heap)
        if current not in en_frontera:
            continue

        en_frontera.remove(current)

        # Marcar como explorado
        closed_set.add(current)
        orden_exploracion.append(('cerrado', current))

        # Verificar si llegamos al objetivo
        if problema.es_objetivo(current):
            # Reconstruir camino
            camino = []
            nodo_actual = current
            while nodo_actual in came_from:
                camino.append(nodo_actual)
                nodo_actual = came_from[nodo_actual]
            camino.append(problema.estado_inicial)
            camino.reverse()

            # El costo total debe ser la suma de los costos de cada movimiento en el camino
            costo_total = 0
            for i in range(1, len(camino)):
                tipo_terreno = problema.laberinto[camino[i].fila][camino[i].columna]
                costo_total += problema.agente.costo_movimiento(tipo_terreno)

            problema.costo_acumulado = costo_total

            return camino, en_frontera, closed_set, orden_exploracion, arbol_busqueda

        # Explorar vecinos
        for accion, neighbor in problema.obtener_acciones(current):
            if neighbor in closed_set:
                continue

            # Calcular el costo del terreno para este movimiento
            costo_terreno = problema.agente.costo_movimiento(problema.laberinto[neighbor.fila][neighbor.columna])

            # Acumular el costo: g_score actual + costo del nuevo terreno
            tentative_g = g_score[current] + costo_terreno

            # Si es un nuevo nodo o encontramos un mejor camino
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                # Actualizar camino y costos
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + problema.heuristica(neighbor)

                # Siempre registrar en el árbol de búsqueda cuando consideramos un vecino
                arbol_busqueda[current].append(neighbor)

                # Si es un nuevo nodo para la frontera
                if neighbor not in en_frontera:
                    en_frontera.add(neighbor)
                    orden_exploracion.append(('abierto', neighbor))
                    heapq.heappush(frontera, (f_score, contador, neighbor))
                    contador += 1
                else:
                    # Actualizar prioridad agregando una nueva entrada
                    heapq.heappush(frontera, (f_score, contador, neighbor))
                    contador += 1

    # No se encontró solución
    return None, en_frontera, closed_set, orden_exploracion, arbol_busqueda