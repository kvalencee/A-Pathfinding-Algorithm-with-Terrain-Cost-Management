import pygame
import numpy as np
from core.estado import Estado

# Definición de colores
COLORES = {
    0: (128, 128, 128),  # Montaña - Gris
    1: (210, 180, 140),  # Tierra - Marrón claro
    2: (0, 105, 148),  # Agua - Azul oscuro
    3: (194, 178, 128),  # Arena - Beige
    4: (34, 139, 34),  # Bosque - Verde
    'oculto': (50, 50, 50),
    'agente': (255, 0, 0),
    'objetivo': (0, 255, 0),
    'texto': (255, 255, 255),
    'borde': (0, 0, 0),
    'nodo_abierto': (0, 255, 255),  # Cian para nodos abiertos
    'nodo_cerrado': (255, 165, 0),  # Naranja para nodos cerrados
    'camino': (255, 215, 0)  # Dorado para el camino solución
}


def inicializar_ui(laberinto, titulo="Exploración de Agente"):
    """Inicializa la interfaz gráfica
    Args:
        laberinto: Matriz del laberinto
        titulo: Título de la ventana
    Returns:
        screen: Superficie de Pygame
        font: Fuente para texto
        cell_size: Tamaño de cada celda
        margin: Margen general
    """
    cell_size = 40
    margin = 20
    map_width = len(laberinto[0]) * cell_size
    map_height = len(laberinto) * cell_size

    # Ventana más ancha para mostrar ambos mapas
    width = map_width * 2 + margin * 3
    height = map_height + margin * 2 + 250  # Espacio adicional para información

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(titulo)
    font = pygame.font.SysFont('Arial', 16)
    title_font = pygame.font.SysFont('Arial', 24, bold=True)

    return screen, font, title_font, cell_size, margin


def dibujar_mapa(screen, laberinto, problema, font, cell_size, x_offset, margin,
                 mostrar_heuristica=True, nodos_abiertos=None, nodos_cerrados=None):
    nodos_abiertos = nodos_abiertos or set()
    nodos_cerrados = nodos_cerrados or set()

    for fila in range(len(laberinto)):
        for columna in range(len(laberinto[0])):
            x = x_offset + columna * cell_size
            y = margin + fila * cell_size
            rect = pygame.Rect(x, y, cell_size, cell_size)

            # Color base del terreno
            color = COLORES[laberinto[fila][columna]] if problema.mapa_visible[fila][columna] else COLORES['oculto']
            pygame.draw.rect(screen, color, rect)

            # Estado actual
            estado = Estado(fila, columna)
            es_abierto = estado in nodos_abiertos
            es_cerrado = estado in nodos_cerrados

            # Mostrar heurística en celdas visibles
            if problema.mapa_visible[fila][columna] and mostrar_heuristica:  # Cambiado de mostrar_info a mostrar_heuristica
                h = problema.heuristica(estado)
                texto_h = font.render(str(h), True, COLORES['texto'])
                screen.blit(texto_h, (x + 5, y + 5))

                # Marcadores de nodos
                if es_abierto:
                    pygame.draw.rect(screen, COLORES['nodo_abierto'],
                                   (x + cell_size - 20, y + 5, 15, 15))
                    texto_o = font.render("O", True, (0, 0, 0))
                    screen.blit(texto_o, (x + cell_size - 18, y + 5))
                elif es_cerrado:
                    pygame.draw.rect(screen, COLORES['nodo_cerrado'],
                                   (x + cell_size - 20, y + 5, 15, 15))
                    texto_x = font.render("X", True, (0, 0, 0))
                    screen.blit(texto_x, (x + cell_size - 18, y + 5))

            pygame.draw.rect(screen, COLORES['borde'], rect, 1)
def dibujar_informacion(screen, problema, font, title_font, width, margin, y_offset):
    """Muestra la información del agente, controles y costo acumulado"""
    # Título del agente
    titulo = title_font.render(f"Agente: {problema.agente.nombre}", True, COLORES['texto'])
    screen.blit(titulo, (margin, y_offset))

    # Información de posición
    estado = problema.estado_actual if hasattr(problema, 'estado_actual') else problema.estado_inicial
    info_pos = font.render(
        f"Posición: ({estado.fila}, {estado.columna}) | Dirección: {estado.direccion}",
        True,
        COLORES['texto']
    )
    screen.blit(info_pos, (margin, y_offset + 30))

    # Costo acumulado
    if hasattr(problema, 'camino_solucion') and problema.camino_solucion:
        costo_total = sum(
            problema.agente.costo_movimiento(problema.laberinto[e.fila][e.columna])
            for e in problema.camino_solucion[1:]
        )
        texto_costo = font.render(f"Costo total del camino: {costo_total}", True, COLORES['texto'])
    else:
        texto_costo = font.render(f"Costo acumulado: {getattr(problema, 'costo_acumulado', 0)}", True, COLORES['texto'])
    screen.blit(texto_costo, (margin, y_offset + 60))


def dibujar_objetivo(screen, objetivo, cell_size, x_offset, margin):
    """Dibuja un objetivo en el mapa
    Args:
        screen: Superficie de Pygame
        objetivo: Estado objetivo
        cell_size: Tamaño de la celda
        x_offset: Desplazamiento horizontal
        margin: Margen superior
    """
    x = x_offset + objetivo.columna * cell_size
    y = margin + objetivo.fila * cell_size

    # Dibujar objetivo (círculo)
    pygame.draw.circle(
        screen,
        COLORES['objetivo'],
        (x + cell_size // 2, y + cell_size // 2),
        cell_size // 3
    )


def dibujar_agente(screen, estado, cell_size, x_offset, margin):
    """Dibuja al agente en su posición actual con indicador de dirección

    Args:
        screen: Superficie de Pygame
        estado: Estado actual del agente
        cell_size: Tamaño de cada celda
        x_offset: Desplazamiento horizontal
        margin: Margen superior
    """
    # Coordenadas base
    x = x_offset + estado.columna * cell_size
    y = margin + estado.fila * cell_size

    # Cuerpo del agente (cuadrado rojo)
    cuerpo_rect = pygame.Rect(
        x + cell_size // 4,
        y + cell_size // 4,
        cell_size // 2,
        cell_size // 2
    )
    pygame.draw.rect(screen, COLORES['agente'], cuerpo_rect)

    # Indicador de dirección (triángulo negro)
    centro_x = x + cell_size // 2
    centro_y = y + cell_size // 2
    tamaño = cell_size // 4  # Tamaño del indicador

    if estado.direccion == "arriba":
        puntos = [
            (centro_x, centro_y - tamaño),  # Punta arriba
            (centro_x - tamaño, centro_y + tamaño),  # Esquina inferior izquierda
            (centro_x + tamaño, centro_y + tamaño)  # Esquina inferior derecha
        ]
    elif estado.direccion == "abajo":
        puntos = [
            (centro_x, centro_y + tamaño),  # Punta abajo
            (centro_x - tamaño, centro_y - tamaño),  # Esquina superior izquierda
            (centro_x + tamaño, centro_y - tamaño)  # Esquina superior derecha
        ]
    elif estado.direccion == "izquierda":
        puntos = [
            (centro_x - tamaño, centro_y),  # Punta izquierda
            (centro_x + tamaño, centro_y - tamaño),  # Esquina superior derecha
            (centro_x + tamaño, centro_y + tamaño)  # Esquina inferior derecha
        ]
    else:  # derecha (por defecto si no coincide)
        puntos = [
            (centro_x + tamaño, centro_y),  # Punta derecha
            (centro_x - tamaño, centro_y - tamaño),  # Esquina superior izquierda
            (centro_x - tamaño, centro_y + tamaño)  # Esquina inferior izquierda
        ]

    pygame.draw.polygon(screen, COLORES['borde'], puntos)



def esperar_tecla():
    """Espera hasta que el usuario presione una tecla o cierre la ventana
    Returns:
        bool: True si se presionó una tecla, False si se cerró la ventana
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                return True