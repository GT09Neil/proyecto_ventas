class DetalleVenta:
    def __init__(self, id_detalle=None, id_venta=None, id_producto=None, cantidad=0, precio_unitario=0.0, subtotal=0.0):
        self.id_detalle = id_detalle
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal

    def __str__(self):
        return f"Producto {self.id_producto} x {self.cantidad} = ${self.subtotal}"
