class Cuota:
    def __init__(
        self,
        id_cuota=None,
        id_credito=None,
        numero=0,
        fecha_programada=None,
        valor_programado=0.0,
        valor_pagado=0.0,
        fecha_pago=None,
        estado="Pendiente",
    ):
        self.id_cuota = id_cuota
        self.id_credito = id_credito
        self.numero = numero
        self.fecha_programada = fecha_programada
        self.valor_programado = valor_programado
        self.valor_pagado = valor_pagado
        self.fecha_pago = fecha_pago
        self.estado = estado

    def __str__(self):
        return f"Cuota {self.numero} - Crédito {self.id_credito} - Estado {self.estado}"



