from typing import List

from db_connection import get_connection
from modelos.detalle_venta import DetalleVenta


class DetalleVentaDAO:
    @staticmethod
    def agregar(detalle: DetalleVenta):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario)
            VALUES (?, ?, ?, ?)
        """,
            (
                detalle.id_venta,
                detalle.id_producto,
                detalle.cantidad,
                detalle.precio_unitario,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def listar_por_venta(id_venta: int) -> List[DetalleVenta]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_detalle, id_venta, id_producto, cantidad, precio_unitario, subtotal
            FROM DetalleVenta
            WHERE id_venta = ?
        """,
            (id_venta,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [DetalleVenta(*row) for row in rows]

    @staticmethod
    def eliminar_por_venta(id_venta: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DetalleVenta WHERE id_venta = ?", (id_venta,))
        conn.commit()
        conn.close()
