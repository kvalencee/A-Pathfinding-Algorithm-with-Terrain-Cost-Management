class Estado:
    def __init__(self, fila, columna, direccion='derecha'):
        self.fila = fila
        self.columna = columna
        self.direccion = direccion  # 'arriba', 'abajo', 'izquierda', 'derecha'

    def __str__(self):
        return f"({self.fila}, {self.columna}, {self.direccion})"

    def __eq__(self, otro):
        return (self.fila == otro.fila and
                self.columna == otro.columna and
                self.direccion == otro.direccion)

    def __hash__(self):
        return hash((self.fila, self.columna, self.direccion))

    def __lt__(self, otro):
        # Definimos un orden arbitrario para que heapq pueda comparar
        return (self.fila, self.columna, self.direccion) < (otro.fila, otro.columna, otro.direccion)