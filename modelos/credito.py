class Credito:
    def __init__(
        self,
        id_credito=None,
        id_venta=None,
        cuota_inicial=0.0,
        saldo=0.0,
        meses=0,
        interes=0.0,
        estado="Activo",
    ):
        self.id_credito = id_credito
        self.id_venta = id_venta
        self.cuota_inicial = cuota_inicial
        self.saldo = saldo
        self.meses = meses
        self.interes = interes
        self.estado = estado

    def __str__(self):
        return f"Crédito {self.id_credito} - Venta {self.id_venta} - Saldo {self.saldo}"



