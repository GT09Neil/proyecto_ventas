from __future__ import annotations

from typing import Callable, Iterable, List

from dao.categoria_dao import CategoriaDAO
from dao.usuario_dao import UsuarioDAO
from dao.cliente_dao import ClienteDAO
from dao.producto_dao import ProductoDAO
from modelos.categoria import Categoria
from modelos.usuario import Usuario
from modelos.cliente import Cliente
from modelos.producto import Producto


class DataInitializer:
    """Crea registros base cuando la base de datos está vacía."""

    _CATEGORIAS_BASE: Iterable[dict] = (
        {"nombre": "Audio", "iva": 0.16, "utilidad": 0.35},
        {"nombre": "Video", "iva": 0.19, "utilidad": 0.39},
        {"nombre": "Tecnología", "iva": 0.12, "utilidad": 0.40},
        {"nombre": "Cocina", "iva": 0.12, "utilidad": 0.35},
    )

    _ADMIN_DEFAULT = {
        "cedula": "9999999999",
        "nombre": "Administrador General",
        "email": "admin@ventas-electro.com",
        "password": "Admin*123",
    }

    _CLIENTE_DEFAULT = {
        "cedula": "1000000000",
        "nombre": "Cliente Demo",
        "direccion": "Calle 123 #45-67",
        "telefono": "3000000000",
        "email": "cliente.demo@ventas-electro.com",
    }

    _PRODUCTO_DEFAULT = {
        "codigo": "PRD-0001",
        "nombre": "Televisor LED 55\"",
        "valor_adquisicion": 1500000.0,
        "valor_venta": 2250000.0,
        "stock": 15,
    }

    def __init__(self, logger: Callable[[str], None] | None = print) -> None:
        self._logger = logger
        self._errores: List[str] = []

    @property
    def errores(self) -> List[str]:
        return self._errores

    def run(self) -> None:
        self._log("Verificando datos base...")
        self._asegurar_categorias()
        self._asegurar_usuario_administrador()
        self._asegurar_cliente_demo()
        self._asegurar_producto_demo()
        self._log("Verificación de datos base finalizada.")

    # ------------------------------------------------------------------ utils
    def _log(self, mensaje: str) -> None:
        if self._logger:
            self._logger(mensaje)

    def _registrar_error(self, contexto: str, error: Exception) -> None:
        mensaje = f"{contexto}: {error}"
        self._errores.append(mensaje)
        self._log(f"[ERROR] {mensaje}")

    # ----------------------------------------------------------- seed helpers
    def _asegurar_categorias(self) -> None:
        try:
            existentes = {cat.nombre.lower() for cat in CategoriaDAO.listar()}
        except Exception as error:
            self._registrar_error("Categorías", error)
            return

        creadas = 0
        for datos in self._CATEGORIAS_BASE:
            if datos["nombre"].lower() in existentes:
                continue
            try:
                CategoriaDAO.crear(
                    Categoria(
                        nombre=datos["nombre"],
                        iva=datos["iva"],
                        utilidad=datos["utilidad"],
                    )
                )
                creadas += 1
            except Exception as error:
                self._registrar_error(f"Crear categoría {datos['nombre']}", error)
        if creadas:
            self._log(f"Categorías base creadas: {creadas}")

    def _asegurar_usuario_administrador(self) -> None:
        try:
            usuarios = UsuarioDAO.listar()
        except Exception as error:
            self._registrar_error("Usuarios", error)
            return

        existe_admin = any(usuario.rol == 1 for usuario in usuarios)
        if existe_admin:
            return

        admin_cfg = self._ADMIN_DEFAULT
        self._log("No se encontró administrador. Creando usuario administrador por defecto.")
        try:
            usuario = Usuario(
                cedula=admin_cfg["cedula"],
                nombre=admin_cfg["nombre"],
                email=admin_cfg["email"],
                rol=1,
                estado="Activo",
            )
            UsuarioDAO.crear(usuario, admin_cfg["password"])
        except Exception as error:
            self._registrar_error("Crear usuario administrador", error)

    def _asegurar_cliente_demo(self) -> None:
        try:
            clientes = ClienteDAO.listar()
        except Exception as error:
            self._registrar_error("Clientes", error)
            return

        if clientes:
            return

        cfg = self._CLIENTE_DEFAULT
        self._log("No se encontraron clientes. Creando cliente de demostración.")
        try:
            ClienteDAO.agregar(
                Cliente(
                    nombre=cfg["nombre"],
                    cedula=cfg["cedula"],
                    direccion=cfg["direccion"],
                    telefono=cfg["telefono"],
                    email=cfg["email"],
                )
            )
        except Exception as error:
            self._registrar_error("Crear cliente demo", error)

    def _asegurar_producto_demo(self) -> None:
        try:
            productos = ProductoDAO.listar()
        except Exception as error:
            self._registrar_error("Productos", error)
            return

        if productos:
            return

        try:
            categorias = CategoriaDAO.listar()
        except Exception as error:
            self._registrar_error("Listar categorías para producto demo", error)
            return

        if not categorias:
            self._log("Sin categorías disponibles, se omite la creación de producto demo.")
            return

        categoria_id = None
        for preferida in ("tecnología", "technology", "video", "audio"):
            categoria_id = next((cat.id_categoria for cat in categorias if cat.nombre.lower() == preferida), None)
            if categoria_id:
                break
        if categoria_id is None:
            categoria_id = categorias[0].id_categoria

        cfg = self._PRODUCTO_DEFAULT
        self._log("No se encontraron productos. Creando producto de demostración.")
        try:
            ProductoDAO.agregar(
                Producto(
                    codigo=cfg["codigo"],
                    nombre=cfg["nombre"],
                    id_categoria=categoria_id,
                    valor_adquisicion=cfg["valor_adquisicion"],
                    valor_venta=cfg["valor_venta"],
                    stock=cfg["stock"],
                )
            )
        except Exception as error:
            self._registrar_error("Crear producto demo", error)


