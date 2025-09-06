from db_connection import get_connection
from modelos.detalle_venta import DetalleVenta

class DetalleVentaDAO:

    @staticmethod
    def agregar(detalle: DetalleVenta):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (detalle.id_venta, detalle.id_producto, detalle.cantidad, detalle.precio_unitario, detalle.subtotal))
        conn.commit()
        conn.close()
