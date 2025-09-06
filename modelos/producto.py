class Producto:
    def __init__(self, id_producto=None, codigo="", nombre="", id_categoria=None, valor_adquisicion=0.0, valor_venta=0.0, stock=0):
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.id_categoria = id_categoria
        self.valor_adquisicion = valor_adquisicion
        self.valor_venta = valor_venta
        self.stock = stock

    def __str__(self):
        return f"{self.nombre} ({self.codigo}) - ${self.valor_venta}"
