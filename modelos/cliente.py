class Cliente:
    def __init__(self, id_cliente=None, nombre="", cedula="", direccion="", telefono="", email=""):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.cedula = cedula
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"
