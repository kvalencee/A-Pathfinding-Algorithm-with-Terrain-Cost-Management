import numpy as np
import pygame
import sys
from core.estado import Estado
from core.accion import Accion
from core.problema import Problema
from core.astar import a_estrella
from agentes.basicos import crear_monkey, crear_octopus
from ui.pygame_ui import (
    inicializar_ui,
    dibujar_mapa,
    dibujar_informacion,  # Asegúrate de incluir esta
    esperar_tecla, COLORES, dibujar_agente, dibujar_objetivo
)


def cargar_laberinto():
    # Mapa de ejemplo 15x15
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


# En la función main():
def main():
    # Configuración inicial
    laberinto = cargar_laberinto()
    screen, font, title_font, cell_size, margin = inicializar_ui(laberinto)
    width = len(laberinto[0]) * cell_size * 2 + margin * 3

    agente = crear_monkey()  # Agente básico sin habilidades especiales
    estado_inicial = Estado(1, 1)
    estado_objetivo = Estado(7, 10)

    problema = Problema(estado_inicial, [estado_objetivo], laberinto, agente)
    problema.camino_solucion = a_estrella(problema)

    # Bucle principal
    paso_a_paso = True
    indice_camino = 0
    running = True

    while running:
        # Actualizar posición y visión
        if problema.camino_solucion and indice_camino < len(problema.camino_solucion):
            problema.estado_actual = problema.camino_solucion[indice_camino]
            problema.actualizar_vision(problema.estado_actual)

        # Dibujar todo
        screen.fill((0, 0, 0))

        # Mapa explorado (izquierda)
        dibujar_mapa(screen, laberinto, problema, font, cell_size, margin, margin)

        # Mapa completo de referencia (derecha)
        problema_temp = Problema(estado_inicial, [estado_objetivo], laberinto, agente)
        problema_temp.mapa_visible = np.ones_like(laberinto)
        dibujar_mapa(screen, laberinto, problema_temp, font, cell_size,
                     margin * 2 + len(laberinto[0]) * cell_size, margin, False)

        # Información
        y_offset = len(laberinto) * cell_size + margin
        info_texto = [
            f"Agente: {agente.nombre}",
            f"Posición: ({problema.estado_actual.fila}, {problema.estado_actual.columna})",
            f"Costo acumulado: {problema.costo_acumulado}",
            "[ESPACIO] Paso a paso/Automático",
            "[FLECHA DERECHA] Avanzar paso",
            "[R] Reiniciar",
            "[ESC] Salir"
        ]

        for i, texto in enumerate(info_texto):
            render = font.render(texto, True, COLORES['texto'])
            screen.blit(render, (margin, y_offset + i * 25))

        pygame.display.flip()

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paso_a_paso = not paso_a_paso
                elif event.key == pygame.K_RIGHT and paso_a_paso:
                    if indice_camino < len(problema.camino_solucion) - 1:
                        indice_camino += 1
                elif event.key == pygame.K_r:
                    # Reiniciar completamente
                    problema = Problema(estado_inicial, [estado_objetivo], laberinto, agente)
                    problema.camino_solucion = a_estrella(problema)
                    indice_camino = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Avance automático
        if not paso_a_paso and indice_camino < len(problema.camino_solucion) - 1:
            indice_camino += 1
            pygame.time.delay(300)  # Pausa para visualización

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()