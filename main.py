import numpy as np
import pygame
import sys
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from core.estado import Estado
from core.problema import Problema
from core.astar import a_estrella
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
    plt.figure(figsize=(25, 15))
    G = nx.DiGraph()

    estilo_normal = {'edge_color': 'gray', 'width': 1, 'alpha': 0.7}
    estilo_solucion = {'edge_color': 'red', 'width': 3, 'style': 'dashed', 'alpha': 1}
    estilo_nodo = {'node_size': 1200, 'node_color': 'lightblue', 'alpha': 0.9}

    for padre, hijos in arbol_busqueda.items():
        for hijo in hijos:
            acciones = [a for a, e in problema.obtener_acciones(padre) if e == hijo]
            g = sum(a.costo for a in acciones) if acciones else 0
            h = problema.heuristica(hijo)
            f = g + h

            G.add_edge(
                str(padre),
                str(hijo),
                g=g,
                h=h,
                f=f,
                label=f"g={g:.1f}\nh={h:.1f}\nf={f:.1f}"
            )

    pos = nx.spring_layout(G, k=0.8, iterations=200, seed=42)

    nx.draw_networkx_nodes(G, pos, **estilo_nodo)
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edges(G, pos, **estilo_normal, arrowstyle='->', arrowsize=15)

    if camino_solucion:
        edges_camino = [(str(camino_solucion[i]), str(camino_solucion[i + 1]))
                        for i in range(len(camino_solucion) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges_camino, **estilo_solucion, arrowstyle='->', arrowsize=20)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, bbox=dict(alpha=0.7))

    leyenda = [
        Line2D([0], [0], color='red', linestyle='--', linewidth=3, label='Camino solución'),
        Line2D([0], [0], color='gray', linewidth=1, label='Exploración normal'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label='Nodo')
    ]

    plt.legend(handles=leyenda, loc='upper right')
    plt.title("Árbol de Búsqueda A*\n(g = costo real, h = heurística, f = g + h)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('arbol_busqueda_a_estrella.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Árbol de búsqueda guardado como 'arbol_busqueda_a_estrella.png'")


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

    camino_solucion, nodos_abiertos, nodos_cerrados, orden_exploracion, arbol_busqueda = a_estrella(problema)

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