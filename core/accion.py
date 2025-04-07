class Accion:
    def __init__(self, nombre, costo=1):
        self.nombre = nombre
        self.costo = costo

    def __str__(self):
        return f"{self.nombre} (costo: {self.costo})"

    def __repr__(self):
        return self.__str__()