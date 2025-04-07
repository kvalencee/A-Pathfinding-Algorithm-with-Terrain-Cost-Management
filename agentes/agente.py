from core.accion import Accion

class Agente:
    def __init__(self, nombre, tipo, habilidades):
        self.nombre = nombre
        self.tipo = tipo  # 'monkey' o 'octopus'
        self.habilidades = habilidades
        self.historial = []
        self.camino_visitado = set()
        self.puntos_decision = set()
        self.vision_alcance = 1
        self.vision_omni_activada = False
        self.cooldown_omni = 0

    def puede_realizar_accion(self, accion):
        """Determina si el agente puede realizar una acción específica"""
        if accion.nombre == 'girar_izquierda':
            return self.habilidades.get('puede_girar_izquierda', True)
        elif accion.nombre == 'girar_derecha':
            return self.habilidades.get('puede_girar_derecha', True)
        return True

    def puede_entrar(self, tipo_terreno):
        """Verifica si el agente puede entrar a un tipo de terreno"""
        return self.habilidades['puede_entrar'].get(tipo_terreno, False)

    def costo_movimiento(self, tipo_terreno):
        """Obtiene el costo de moverse en un tipo de terreno"""
        return self.habilidades['costos'].get(tipo_terreno, 1)

    def registrar_decision(self, estado, accion, resultado):
        """Registra una decisión tomada por el agente"""
        self.historial.append({
            'estado': estado,
            'accion': accion,
            'resultado': resultado,
            'costo': accion.costo
        })
        self.camino_visitado.add((estado.fila, estado.columna))

        # Registrar puntos de decisión
        acciones_posibles = [a for a in ['avanzar', 'girar_izquierda', 'girar_derecha']
                          if self.puede_realizar_accion(Accion(a))]
        if len(acciones_posibles) > 1:
            self.puntos_decision.add((estado.fila, estado.columna))

    def reiniciar(self):
        """Reinicia el estado del agente"""
        self.historial = []
        self.camino_visitado = set()
        self.puntos_decision = set()
        self.vision_omni_activada = False
        self.cooldown_omni = 0