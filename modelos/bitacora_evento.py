class BitacoraEvento:
    def __init__(self, id_bitacora=None, id_usuario=None, tipo_evento="", fecha_hora=None, detalle=None):
        self.id_bitacora = id_bitacora
        self.id_usuario = id_usuario
        self.tipo_evento = tipo_evento
        self.fecha_hora = fecha_hora
        self.detalle = detalle

    def __str__(self):
        return f"[{self.fecha_hora}] Usuario {self.id_usuario} - {self.tipo_evento}: {self.detalle or ''}"



