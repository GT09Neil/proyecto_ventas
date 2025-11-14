class Usuario:
    def __init__(
        self,
        id_usuario=None,
        cedula="",
        nombre="",
        email="",
        rol=3,
        estado="Activo",
        password_hash=None,
        fecha_creacion=None,
        ultimo_acceso=None,
    ):
        self.id_usuario = id_usuario
        self.cedula = cedula
        self.nombre = nombre
        self.email = email
        self.rol = rol
        self.estado = estado
        self.password_hash = password_hash
        self.fecha_creacion = fecha_creacion
        self.ultimo_acceso = ultimo_acceso

    def __str__(self):
        return f"{self.nombre} ({self.cedula}) - Rol {self.rol}"



