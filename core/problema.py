import numpy as np
from core.estado import Estado
from core.accion import Accion
from collections import defaultdict

class Problema:
    def __init__(self, estado_inicial, estados_objetivos, laberinto, agente):
        self.estado_inicial = estado_inicial
        self.estados_objetivos = estados_objetivos
        self.laberinto = laberinto
        self.agente = agente
        self.mapa_visible = np.zeros_like(laberinto)
        self.camino_solucion = []
        self.costo_acumulado = 0
        self.actualizar_vision(estado_inicial)

    def actualizar_vision(self, estado):
        """Revela la celda actual y las adyacentes"""
        fila, columna = estado.fila, estado.columna
        self.mapa_visible[fila][columna] = 1

        # Revelar celdas adyacentes
        for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nueva_fila, nueva_col = fila + df, columna + dc
            if (0 <= nueva_fila < len(self.laberinto) and
                0 <= nueva_col < len(self.laberinto[0])):
                self.mapa_visible[nueva_fila][nueva_col] = 1

    def es_objetivo(self, estado):
        return any(estado.fila == obj.fila and estado.columna == obj.columna
                   for obj in self.estados_objetivos)

    def obtener_acciones(self, estado):
        """Devuelve movimientos válidos con sus costos reales"""
        acciones = []
        fila, columna = estado.fila, estado.columna

        movimientos = [
            ('arriba', -1, 0),
            ('abajo', 1, 0),
            ('izquierda', 0, -1),
            ('derecha', 0, 1)
        ]

        for nombre, df, dc in movimientos:
            nueva_fila = fila + df
            nueva_col = columna + dc

            if (0 <= nueva_fila < len(self.laberinto) and \
               (0 <= nueva_col < len(self.laberinto[0]))) and \
               self.agente.puede_entrar(self.laberinto[nueva_fila][nueva_col]):
                costo = self.agente.costo_movimiento(self.laberinto[nueva_fila][nueva_col])
                acciones.append((Accion(nombre, costo), Estado(nueva_fila, nueva_col, nombre)))

        return acciones

    def heuristica(self, estado):
        """Distancia Manhattan al objetivo más cercano"""
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