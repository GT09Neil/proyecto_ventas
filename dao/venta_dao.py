from typing import List, Optional

from db_connection import get_connection
from modelos.venta import Venta


class VentaDAO:
    @staticmethod
    def agregar(venta: Venta) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Venta (id_cliente, fecha, tipo, total, id_usuario, estado)
            OUTPUT INSERTED.id_venta
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (venta.id_cliente, venta.fecha, venta.tipo_pago, venta.total, venta.id_usuario, venta.estado),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return nuevo_id

    @staticmethod
    def listar() -> List[Venta]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_venta, id_cliente, fecha, tipo, total, id_usuario, estado
            FROM Venta
            ORDER BY fecha DESC
        """
        )
        rows = cursor.fetchall()
        conn.close()
        ventas = []
        for row in rows:
            ventas.append(
                Venta(
                    id_venta=row.id_venta,
                    id_cliente=row.id_cliente,
                    fecha=row.fecha,
                    tipo_pago=row.tipo,
                    total=float(row.total or 0),
                    id_usuario=row.id_usuario,
                    estado=row.estado,
                )
            )
        return ventas

    @staticmethod
    def obtener_por_id(id_venta: int) -> Optional[Venta]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_venta, id_cliente, fecha, tipo, total, id_usuario, estado
            FROM Venta
            WHERE id_venta = ?
        """,
            (id_venta,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Venta(
            id_venta=row.id_venta,
            id_cliente=row.id_cliente,
            fecha=row.fecha,
            tipo_pago=row.tipo,
            total=float(row.total or 0),
            id_usuario=row.id_usuario,
            estado=row.estado,
        )

    @staticmethod
    def actualizar(venta: Venta) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Venta
            SET id_cliente = ?, fecha = ?, tipo = ?, total = ?, id_usuario = ?, estado = ?
            WHERE id_venta = ?
        """,
            (
                venta.id_cliente,
                venta.fecha,
                venta.tipo_pago,
                venta.total,
                venta.id_usuario,
                venta.estado,
                venta.id_venta,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(id_venta: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Venta WHERE id_venta = ?", (id_venta,))
        conn.commit()
        conn.close()
