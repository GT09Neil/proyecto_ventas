class Venta:
    def __init__(
        self,
        id_venta=None,
        id_cliente=None,
        fecha=None,
        tipo_pago="Contado",
        total=0.0,
        id_usuario=None,
        estado="Registrada",
    ):
        self.id_venta = id_venta
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.tipo_pago = tipo_pago  # "Contado" o "Crédito"
        self.total = total
        self.id_usuario = id_usuario
        self.estado = estado

    def __str__(self):
        return f"Venta {self.id_venta} - Cliente {self.id_cliente} - Total ${self.total}"
