import numpy as np
from core.estado import Estado  # <-- Añade esta importación
from core.accion import Accion
from collections import defaultdict


class Problema:
    def __init__(self, estado_inicial, estados_objetivos, laberinto, agente):
        self.estado_inicial = estado_inicial
        self.estados_objetivos = estados_objetivos
        self.laberinto = laberinto
        self.agente = agente
        # Mapa completamente oculto al inicio
        self.mapa_visible = np.zeros_like(laberinto)
        self.camino_solucion = []
        self.costo_acumulado = 0
        # Revelar solo la posición inicial y adyacentes
        self.actualizar_vision(estado_inicial)

    def actualizar_vision(self, estado):
        """Revela la celda actual y las adyacentes"""
        for fila in range(max(0, estado.fila-1), min(len(self.laberinto), estado.fila+2)):
            for col in range(max(0, estado.columna-1), min(len(self.laberinto[0]), estado.columna+2)):
                self.mapa_visible[fila][col] = 1

    def es_objetivo(self, estado):
        return any(estado.fila == obj.fila and estado.columna == obj.columna
                   for obj in self.estados_objetivos)

    def sensar_camino(self, estado):
        fila, columna = estado.fila, estado.columna

        if self.agente.vision_omni_activada:
            self._sensar_omni(fila, columna)
            self.agente.vision_omni_activada = False
            self.agente.cooldown_omni = 5
        elif self.agente.habilidades.get('vision_lejana', False):
            self._sensar_lejano(estado)
        else:
            self._sensar_normal(estado)

        return self._camino_despejado(estado)

    def _sensar_omni(self, fila, columna):
        direcciones = ['arriba', 'abajo', 'izquierda', 'derecha']
        alcance = 3
        for direccion in direcciones:
            for i in range(1, alcance + 1):
                if direccion == "arriba":
                    f, c = fila - i, columna
                elif direccion == "abajo":
                    f, c = fila + i, columna
                elif direccion == "izquierda":
                    f, c = fila, columna - i
                elif direccion == "derecha":
                    f, c = fila, columna + i

                if 0 <= f < len(self.laberinto) and 0 <= c < len(self.laberinto[0]):
                    self.mapa_visible[f][c] = 1
                    if not self.agente.puede_entrar(self.laberinto[f][c]):
                        break

    def _sensar_lejano(self, estado):
        fila, columna = estado.fila, estado.columna
        for i in range(1, 4):
            if estado.direccion == "arriba":
                f, c = fila - i, columna
            elif estado.direccion == "abajo":
                f, c = fila + i, columna
            elif estado.direccion == "izquierda":
                f, c = fila, columna - i
            elif estado.direccion == "derecha":
                f, c = fila, columna + i

            if 0 <= f < len(self.laberinto) and 0 <= c < len(self.laberinto[0]):
                self.mapa_visible[f][c] = 1
                if not self.agente.puede_entrar(self.laberinto[f][c]):
                    break

    def _sensar_normal(self, estado):
        fila, columna = estado.fila, estado.columna
        if estado.direccion == "arriba":
            f, c = fila - 1, columna
        elif estado.direccion == "abajo":
            f, c = fila + 1, columna
        elif estado.direccion == "izquierda":
            f, c = fila, columna - 1
        elif estado.direccion == "derecha":
            f, c = fila, columna + 1

        if 0 <= f < len(self.laberinto) and 0 <= c < len(self.laberinto[0]):
            self.mapa_visible[f][c] = 1

    def _camino_despejado(self, estado):
        fila, columna = estado.fila, estado.columna
        if estado.direccion == "arriba":
            nueva_fila, nueva_columna = fila - 1, columna
        elif estado.direccion == "abajo":
            nueva_fila, nueva_columna = fila + 1, columna
        elif estado.direccion == "izquierda":
            nueva_fila, nueva_columna = fila, columna - 1
        elif estado.direccion == "derecha":
            nueva_fila, nueva_columna = fila, columna + 1

        return (0 <= nueva_fila < len(self.laberinto) and
                0 <= nueva_columna < len(self.laberinto[0]) and
                self.agente.puede_entrar(self.laberinto[nueva_fila][nueva_columna]))

    def avanzar(self, estado):
        fila, columna = estado.fila, estado.columna
        rango = self.agente.habilidades.get('rango_movimiento', 1)
        costo_total = 0

        for paso in range(1, rango + 1):
            if estado.direccion == "arriba":
                nueva_fila, nueva_columna = fila - paso, columna
            elif estado.direccion == "abajo":
                nueva_fila, nueva_columna = fila + paso, columna
            elif estado.direccion == "izquierda":
                nueva_fila, nueva_columna = fila, columna - paso
            elif estado.direccion == "derecha":
                nueva_fila, nueva_columna = fila, columna + paso

            if not (0 <= nueva_fila < len(self.laberinto) and
                    0 <= nueva_columna < len(self.laberinto[0]) and
                    self.agente.puede_entrar(self.laberinto[nueva_fila][nueva_columna])):
                if paso == 1:
                    return None, 0
                break

            fila, columna = nueva_fila, nueva_columna
            costo_total += self.agente.costo_movimiento(self.laberinto[fila][columna])

        self.mapa_visible[fila][columna] = 1
        return Estado(fila, columna, estado.direccion), costo_total

    def girar_izquierda(self, estado):
        if not self.agente.puede_realizar_accion(Accion('girar_izquierda')):
            return None, 0

        direcciones = ['arriba', 'izquierda', 'abajo', 'derecha']
        current_idx = direcciones.index(estado.direccion)
        nueva_direccion = direcciones[(current_idx + 1) % 4]
        return Estado(estado.fila, estado.columna, nueva_direccion), 1

    def girar_derecha(self, estado):
        if not self.agente.puede_realizar_accion(Accion('girar_derecha')):
            return None, 0

        direcciones = ['arriba', 'derecha', 'abajo', 'izquierda']
        current_idx = direcciones.index(estado.direccion)
        nueva_direccion = direcciones[(current_idx + 1) % 4]
        return Estado(estado.fila, estado.columna, nueva_direccion), 1

    def obtener_acciones(self, estado):
        acciones = []

        resultado_avanzar, costo_avanzar = self.avanzar(estado)
        if resultado_avanzar is not None:
            acciones.append((Accion('avanzar', costo_avanzar), resultado_avanzar))

        resultado_izquierda, costo_izquierda = self.girar_izquierda(estado)
        if resultado_izquierda is not None:
            acciones.append((Accion('girar_izquierda', costo_izquierda), resultado_izquierda))

        resultado_derecha, costo_derecha = self.girar_derecha(estado)
        if resultado_derecha is not None:
            acciones.append((Accion('girar_derecha', costo_derecha), resultado_derecha))

        return acciones

    def heuristica(self, estado):
        min_dist = float('inf')
        for objetivo in self.estados_objetivos:
            dist = abs(estado.fila - objetivo.fila) + abs(estado.columna - objetivo.columna)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def reiniciar(self):
        self.mapa_visible = np.zeros_like(self.laberinto)
        self.mapa_visible[self.estado_inicial.fila][self.estado_inicial.columna] = 1
        self.camino_solucion = []
        self.costo_acumulado = 0
        self.agente.reiniciar()