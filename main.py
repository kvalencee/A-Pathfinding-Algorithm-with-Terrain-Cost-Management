import numpy as np
import pygame
import sys
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from core.estado import Estado
from core.problema import Problema
from core.astar import a_estrella_corregido
from agentes.basicos import crear_monkey, crear_octopus
from ui.pygame_ui import (
    inicializar_ui,
    dibujar_mapa,
    COLORES, dibujar_agente, dibujar_objetivo,
    dibujar_informacion
)


def cargar_laberinto():
    return np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 2, 2, 1, 1, 1, 4, 4, 4, 1, 0],
        [0, 1, 3, 3, 1, 2, 2, 1, 3, 1, 4, 4, 4, 1, 0],
        [0, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 2, 2, 1, 0, 0, 0, 1, 2, 2, 0, 0, 0, 0, 0],
        [0, 2, 2, 1, 1, 0, 1, 1, 2, 2, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 4, 0, 4, 1, 1, 1, 1, 3, 1, 1, 0],
        [0, 1, 3, 1, 4, 0, 4, 4, 1, 3, 3, 3, 1, 1, 0],
        [0, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])


def seleccionar_agente():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Seleccionar Agente")
    font = pygame.font.SysFont('Arial', 24)

    opciones = [
        ("1 - Mono", crear_monkey),
        ("2 - Pulpo", crear_octopus)
    ]

    screen.fill((0, 0, 0))
    y_pos = 50
    for texto, _ in opciones:
        render = font.render(texto, True, (255, 255, 255))
        screen.blit(render, (150, y_pos))
        y_pos += 50

    instruccion = font.render("Presiona 1 o 2 para elegir", True, (255, 255, 255))
    screen.blit(instruccion, (80, 150))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return crear_monkey()
                elif event.key == pygame.K_2:
                    return crear_octopus()


def seleccionar_posicion(laberinto, mensaje, agente=None):
    pygame.init()
    cell_size = 40
    margin = 20
    width = len(laberinto[0]) * cell_size + margin * 2
    height = len(laberinto) * cell_size + margin * 2 + 50

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(mensaje)
    font = pygame.font.SysFont('Arial', 16)

    validas = np.zeros_like(laberinto, dtype=bool)
    if agente:
        for i in range(len(laberinto)):
            for j in range(len(laberinto[0])):
                validas[i][j] = agente.puede_entrar(laberinto[i][j])
    else:
        validas = laberinto != 0

    while True:
        screen.fill((0, 0, 0))
        for fila in range(len(laberinto)):
            for columna in range(len(laberinto[0])):
                x = margin + columna * cell_size
                y = margin + fila * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)

                color = COLORES[laberinto[fila][columna]]
                if not validas[fila][columna]:
                    color = (color[0] // 2, color[1] // 2, color[2] // 2)

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, COLORES['borde'], rect, 1)

        instruccion = font.render("Haz clic en una celda válida", True, (255, 255, 255))
        screen.blit(instruccion, (margin, height - 30))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                columna = (pos[0] - margin) // cell_size
                fila = (pos[1] - margin) // cell_size

                if (0 <= fila < len(laberinto)) and (0 <= columna < len(laberinto[0])) and validas[fila][columna]:
                    return fila, columna


def visualizar_arbol_a_estrella(problema, arbol_busqueda, camino_solucion):
    plt.figure(figsize=(30, 20))  # Tamaño más grande para mejor visualización
    G = nx.DiGraph()

    # Estilos mejorados
    estilo_normal = {'edge_color': 'gray', 'width': 1.5, 'alpha': 0.7, 'arrowsize': 20}
    estilo_solucion = {'edge_color': '#FF4500', 'width': 4, 'style': 'dashed', 'alpha': 1, 'arrowsize': 25}
    estilo_nodo = {'node_size': 2000, 'node_color': '#ADD8E6', 'alpha': 0.9, 'node_shape': 's'}
    estilo_texto = {'font_size': 10, 'font_weight': 'bold', 'font_family': 'sans-serif'}

    # Primero construimos el grafo sin etiquetas
    for padre, hijos in arbol_busqueda.items():
        for hijo in hijos:
            G.add_edge(str(padre), str(hijo))

    # Calculamos los valores g (costo acumulado desde el inicio) para cada nodo
    g_values = {}
    g_values[str(problema.estado_inicial)] = 0  # El nodo inicial tiene costo 0

    # Función recursiva para calcular g
    def calcular_g_recursivo(nodo_actual_str):
        if nodo_actual_str in g_values:
            return g_values[nodo_actual_str]

        # Encontrar todos los padres posibles para este nodo
        padres = []
        nodo_actual = None

        # Primero tenemos que convertir el string a un objeto Estado
        for estado in arbol_busqueda.keys():
            if str(estado) == nodo_actual_str:
                nodo_actual = estado
                break

        if nodo_actual is None:
            # Si no encontramos el estado, buscamos entre todos los hijos
            for padre, hijos in arbol_busqueda.items():
                for hijo in hijos:
                    if str(hijo) == nodo_actual_str:
                        nodo_actual = hijo
                        break
                if nodo_actual:
                    break

        # Ahora buscamos todos los padres posibles
        for padre, hijos in arbol_busqueda.items():
            if nodo_actual in hijos:
                padres.append(padre)

        # Si no hay padres, es un nodo raíz o huérfano
        if not padres:
            g_values[nodo_actual_str] = float('inf')  # No debería suceder en A*
            return float('inf')

        # Elegimos el padre que da el menor g
        min_g = float('inf')
        for padre in padres:
            # Calcular recursivamente el g del padre si no lo conocemos
            g_padre = calcular_g_recursivo(str(padre))

            # Costo del movimiento desde el padre hasta este nodo
            costo_movimiento = problema.agente.costo_movimiento(
                problema.laberinto[nodo_actual.fila][nodo_actual.columna])

            # Nuevo g potencial
            nuevo_g = g_padre + costo_movimiento

            if nuevo_g < min_g:
                min_g = nuevo_g

        g_values[nodo_actual_str] = min_g
        return min_g

    # Calcular g para todos los nodos
    for node in G.nodes():
        if node not in g_values:
            calcular_g_recursivo(node)

    # Ahora actualizamos las aristas con la información correcta
    for padre, hijos in arbol_busqueda.items():
        padre_str = str(padre)

        for hijo in hijos:
            hijo_str = str(hijo)

            # Obtenemos g acumulado para el nodo hijo
            g = g_values[hijo_str]

            # Calculamos h (heurística) para este nodo
            h = problema.heuristica(hijo)

            # f es g + h
            f = g + h

            # Formateo más limpio de las etiquetas
            label = f"g={g:.1f}\nh={h:.1f}\nf={f:.1f}"

            # Actualizamos la arista con esta información
            G.edges[padre_str, hijo_str]['g'] = g
            G.edges[padre_str, hijo_str]['h'] = h
            G.edges[padre_str, hijo_str]['f'] = f
            G.edges[padre_str, hijo_str]['label'] = label

    # Usar un layout más organizado
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')  # Requiere pygraphviz
    except:
        # Fallback si no está instalado pygraphviz
        pos = nx.spring_layout(G, k=0.9, iterations=100, seed=42)

    # Dibujar elementos
    nx.draw_networkx_nodes(G, pos, **estilo_nodo)

    # Preparar etiquetas de nodos con información de g, h, f
    node_labels = {}
    for node in G.nodes():
        # Si es un nodo hoja, no tendrá etiquetas de arista, así que calculamos los valores
        if G.out_degree(node) == 0:
            g = g_values[node]

            # Convertir el string a objeto Estado para calcular h
            estado_actual = None
            for estado in arbol_busqueda.keys():
                if str(estado) == node:
                    estado_actual = estado
                    break

            if not estado_actual:
                for padre, hijos in arbol_busqueda.items():
                    for hijo in hijos:
                        if str(hijo) == node:
                            estado_actual = hijo
                            break

            h = problema.heuristica(estado_actual) if estado_actual else 0
            f = g + h
            node_labels[node] = f"{node}\ng={g:.1f}, h={h:.1f}, f={f:.1f}"
        else:
            # Para nodos internos, usamos la información de las aristas salientes
            salientes = list(G.out_edges(node))
            if salientes:
                edge = salientes[0]
                g = g_values[node]
                h = G.edges[edge]['h']  # Usamos h de una arista saliente
                f = g + h
                node_labels[node] = f"{node}\ng={g:.1f}, h={h:.1f}, f={f:.1f}"
            else:
                node_labels[node] = node

    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_weight='bold')

    # Dibujar todas las aristas primero (normales)
    nx.draw_networkx_edges(G, pos, **estilo_normal, arrowstyle='->')

    # Resaltar camino solución si existe
    if camino_solucion:
        edges_camino = [(str(camino_solucion[i]), str(camino_solucion[i + 1]))
                        for i in range(len(camino_solucion) - 1)]
        edges_validos = [(u, v) for u, v in edges_camino if G.has_edge(u, v)]
        nx.draw_networkx_edges(G, pos, edgelist=edges_validos, **estilo_solucion, arrowstyle='->')

    # Mejorar las etiquetas de las aristas
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,
        bbox=dict(alpha=0.85, boxstyle='round,pad=0.2', facecolor='white', edgecolor='none')
    )

    # Leyenda más clara
    leyenda = [
        Line2D([0], [0], color='#FF4500', linestyle='--', linewidth=4, label='Camino solución'),
        Line2D([0], [0], color='gray', linewidth=2, label='Exploración normal'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#ADD8E6', markersize=15, label='Nodo')
    ]
    plt.legend(
        handles=leyenda,
        loc='upper right',
        fontsize=12,
        title="Leyenda:",
        title_fontsize=13,
        framealpha=0.9
    )

    # Título más profesional
    plt.title("Árbol de Búsqueda A*\n(g = costo acumulado, h = heurística, f = g + h)",
              fontsize=16, pad=20, fontweight='bold')

    # Ajustes finales
    plt.axis('off')
    plt.tight_layout()

    # Guardar con mayor resolución y calidad
    plt.savefig(
        'arbol_busqueda_a_estrella_mejorado.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )
    plt.close()
    print("Árbol de búsqueda mejorado guardado como 'arbol_busqueda_a_estrella_mejorado.png'")

def main():
    laberinto = cargar_laberinto()
    agente = seleccionar_agente()

    fila_inicial, columna_inicial = seleccionar_posicion(laberinto, "Selecciona Posición Inicial", agente)
    estado_inicial = Estado(fila_inicial, columna_inicial)

    fila_objetivo, columna_objetivo = seleccionar_posicion(laberinto, "Selecciona Posición Objetivo", agente)
    estado_objetivo = Estado(fila_objetivo, columna_objetivo)

    screen, font, title_font, cell_size, margin = inicializar_ui(laberinto)
    width = len(laberinto[0]) * cell_size * 2 + margin * 3

    problema = Problema(estado_inicial, [estado_objetivo], laberinto, agente)
    problema.mapa_visible = np.zeros_like(laberinto)
    problema.mapa_visible[estado_inicial.fila][estado_inicial.columna] = 1
    problema.mapa_visible[estado_objetivo.fila][estado_objetivo.columna] = 1

    camino_solucion, nodos_abiertos, nodos_cerrados, orden_exploracion, arbol_busqueda = a_estrella_corregido(problema)

    if camino_solucion is None:
        print("No se encontró solución!")
        pygame.quit()
        sys.exit()

    problema.camino_solucion = camino_solucion
    visualizar_arbol_a_estrella(problema, arbol_busqueda, camino_solucion)

    running = True
    paso_a_paso = True
    indice_exploracion = 0
    nodos_abiertos_visibles = set()
    nodos_cerrados_visibles = set()
    mostrar_info = True

    indice_camino = 0
    tiempo_ultimo_paso = pygame.time.get_ticks()
    tiempo_entre_pasos = 500
    solucion_encontrada = False

    while running:
        current_time = pygame.time.get_ticks()

        if (not solucion_encontrada and
                (not paso_a_paso or
                 (paso_a_paso and indice_exploracion < len(orden_exploracion)))):

            if indice_exploracion < len(orden_exploracion):
                tipo, estado = orden_exploracion[indice_exploracion]

                if tipo == 'abierto':
                    nodos_abiertos_visibles.add(estado)
                else:
                    if estado in nodos_abiertos_visibles:
                        nodos_abiertos_visibles.remove(estado)
                    nodos_cerrados_visibles.add(estado)

                problema.estado_actual = estado
                problema.actualizar_vision(estado)
                indice_exploracion += 1

                if problema.es_objetivo(estado):
                    solucion_encontrada = True
                    indice_camino = 0
                    tiempo_ultimo_paso = current_time

        screen.fill((0, 0, 0))

        dibujar_mapa(
            screen, laberinto, problema, font, cell_size, margin, margin,
            mostrar_heuristica=mostrar_info,  # Aquí pasamos el valor correcto
            nodos_abiertos=nodos_abiertos_visibles,
            nodos_cerrados=nodos_cerrados_visibles
        )

        if solucion_encontrada and problema.camino_solucion:
            for estado in problema.camino_solucion:
                x = margin + estado.columna * cell_size
                y = margin + estado.fila * cell_size
                pygame.draw.rect(screen, COLORES['camino'], (x, y, cell_size, cell_size), 3)

        dibujar_agente(screen, problema.estado_actual, cell_size, margin, margin)
        dibujar_objetivo(screen, estado_objetivo, cell_size, margin, margin)

        x_offset_right = len(laberinto[0]) * cell_size + margin * 2

        for fila in range(len(laberinto)):
            for columna in range(len(laberinto[0])):
                x = x_offset_right + columna * cell_size
                y = margin + fila * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)

                color = COLORES[laberinto[fila][columna]]
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, COLORES['borde'], rect, 1)

        if problema.camino_solucion:
            for estado in problema.camino_solucion:
                x = x_offset_right + estado.columna * cell_size
                y = margin + estado.fila * cell_size
                pygame.draw.rect(screen, COLORES['camino'], (x, y, cell_size, cell_size), 3)

        if solucion_encontrada and problema.camino_solucion:
            if indice_camino < len(problema.camino_solucion):
                if current_time - tiempo_ultimo_paso >= tiempo_entre_pasos:
                    estado_camino = problema.camino_solucion[indice_camino]
                    dibujar_agente(screen, estado_camino, cell_size, x_offset_right, margin)
                    indice_camino += 1
                    tiempo_ultimo_paso = current_time
            else:
                dibujar_agente(screen, problema.camino_solucion[-1], cell_size, x_offset_right, margin)

        dibujar_objetivo(screen, estado_objetivo, cell_size, x_offset_right, margin)

        y_offset = len(laberinto) * cell_size + margin * 2
        if solucion_encontrada and problema.camino_solucion:
            # Mostrar información con el costo total
            y_offset = len(laberinto) * cell_size + margin * 2
            dibujar_informacion(screen, problema, font, title_font, width, margin, y_offset)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    mostrar_info = not mostrar_info
                elif event.key == pygame.K_SPACE:
                    paso_a_paso = not paso_a_paso
                elif event.key == pygame.K_RIGHT and paso_a_paso:
                    if indice_exploracion < len(orden_exploracion):
                        tipo, estado = orden_exploracion[indice_exploracion]
                        if tipo == 'abierto':
                            nodos_abiertos_visibles.add(estado)
                        else:
                            if estado in nodos_abiertos_visibles:
                                nodos_abiertos_visibles.remove(estado)
                            nodos_cerrados_visibles.add(estado)

                        problema.estado_actual = estado
                        problema.actualizar_vision(estado)
                        indice_exploracion += 1
                elif event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_ESCAPE:
                    running = False

        pygame.time.delay(100)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()