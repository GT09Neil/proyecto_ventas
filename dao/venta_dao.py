from db_connection import get_connection
from modelos.venta import Venta

class VentaDAO:

    @staticmethod
    def agregar(venta: Venta):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Venta (id_cliente, fecha, tipo_pago, total)
            VALUES (?, ?, ?, ?)
        """, (venta.id_cliente, venta.fecha, venta.tipo_pago, venta.total))
        conn.commit()
        conn.close()
