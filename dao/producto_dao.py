from db_connection import get_connection
from modelos.producto import Producto

class ProductoDAO:

    @staticmethod
    def agregar(producto: Producto):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Producto (codigo, nombre, id_categoria, valor_adquisicion, valor_venta, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (producto.codigo, producto.nombre, producto.id_categoria, producto.valor_adquisicion, producto.valor_venta, producto.stock))
        conn.commit()
        conn.close()

    @staticmethod
    def listar():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_producto, codigo, nombre, id_categoria, valor_adquisicion, valor_venta, stock FROM Producto")
        rows = cursor.fetchall()
        conn.close()
        return [Producto(*row) for row in rows]
