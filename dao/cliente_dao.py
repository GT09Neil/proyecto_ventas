from typing import List, Optional

from db_connection import get_connection
from modelos.cliente import Cliente


class ClienteDAO:
    @staticmethod
    def agregar(cliente: Cliente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Cliente (nombre, cedula, direccion, telefono, correo)
            VALUES (?, ?, ?, ?, ?)
        """,
            (cliente.nombre, cliente.cedula, cliente.direccion, cliente.telefono, cliente.email),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def listar() -> List[Cliente]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_cliente, nombre, cedula, direccion, telefono, correo FROM Cliente ORDER BY nombre"
        )
        rows = cursor.fetchall()
        conn.close()
        return [Cliente(*row) for row in rows]

    @staticmethod
    def obtener_por_id(id_cliente: int) -> Optional[Cliente]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_cliente, nombre, cedula, direccion, telefono, correo FROM Cliente WHERE id_cliente=?",
            (id_cliente,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Cliente(*row)

    @staticmethod
    def buscar_por_cedula(cedula: str) -> Optional[Cliente]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_cliente, nombre, cedula, direccion, telefono, correo FROM Cliente WHERE cedula=?",
            (cedula,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Cliente(*row)

    @staticmethod
    def actualizar(cliente: Cliente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Cliente 
            SET nombre=?, cedula=?, direccion=?, telefono=?, correo=?
            WHERE id_cliente=?
        """,
            (
                cliente.nombre,
                cliente.cedula,
                cliente.direccion,
                cliente.telefono,
                cliente.email,
                cliente.id_cliente,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(id_cliente: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cliente WHERE id_cliente=?", (id_cliente,))
        conn.commit()
        conn.close()
