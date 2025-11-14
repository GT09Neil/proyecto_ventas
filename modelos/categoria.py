class Categoria:
    def __init__(self, id_categoria=None, nombre="", iva=0.0, utilidad=0.0):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.iva = iva
        self.utilidad = utilidad

    def __str__(self):
        return f"{self.nombre} (IVA {self.iva}%, Utilidad {self.utilidad}%)"
