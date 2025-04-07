from agentes.agente import Agente

def crear_monkey():
    return Agente("Mono", "monkey", {
        'puede_entrar': {
            0: False,  # Montaña
            1: True,   # Tierra
            2: True,   # Agua
            3: True,   # Arena
            4: True    # Bosque
        },
        'costos': {
            1: 2,  # Tierra
            2: 4,  # Agua
            3: 3,  # Arena
            4: 1   # Bosque
        },
        'puede_girar_izquierda': True,
        'puede_girar_derecha': True,
        'rango_movimiento': 1
    })

def crear_octopus():
    return Agente("Pulpo", "octopus", {
        'puede_entrar': {
            0: False,  # Montaña
            1: True,   # Tierra
            2: True,   # Agua
            3: False,  # Arena
            4: True    # Bosque
        },
        'costos': {
            1: 2,  # Tierra
            2: 1,  # Agua
            4: 3   # Bosque
        },
        'puede_girar_izquierda': True,
        'puede_girar_derecha': True,
        'rango_movimiento': 1
    })