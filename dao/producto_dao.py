from typing import List, Optional

from db_connection import get_connection
from modelos.producto import Producto


class ProductoDAO:
    @staticmethod
    def agregar(producto: Producto):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Producto (codigo, nombre, id_categoria, valor_adquisicion, valor_venta, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                producto.codigo,
                producto.nombre,
                producto.id_categoria,
                producto.valor_adquisicion,
                producto.valor_venta,
                producto.stock,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def listar() -> List[Producto]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_producto, codigo, nombre, id_categoria, valor_adquisicion, valor_venta, stock
            FROM Producto
            ORDER BY nombre
        """
        )
        rows = cursor.fetchall()
        conn.close()
        return [Producto(*row) for row in rows]

    @staticmethod
    def obtener_por_id(id_producto: int) -> Optional[Producto]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_producto, codigo, nombre, id_categoria, valor_adquisicion, valor_venta, stock
            FROM Producto
            WHERE id_producto = ?
        """,
            (id_producto,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Producto(*row)

    @staticmethod
    def actualizar(producto: Producto) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Producto
            SET codigo = ?, nombre = ?, id_categoria = ?, valor_adquisicion = ?, valor_venta = ?, stock = ?
            WHERE id_producto = ?
        """,
            (
                producto.codigo,
                producto.nombre,
                producto.id_categoria,
                producto.valor_adquisicion,
                producto.valor_venta,
                producto.stock,
                producto.id_producto,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(id_producto: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Producto WHERE id_producto = ?", (id_producto,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_codigo(codigo: str) -> Optional[Producto]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_producto, codigo, nombre, id_categoria, valor_adquisicion, valor_venta, stock
            FROM Producto
            WHERE codigo = ?
        """,
            (codigo,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Producto(*row)

    @staticmethod
    def actualizar_stock(id_producto: int, nuevo_stock: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Producto SET stock = ? WHERE id_producto = ?",
            (nuevo_stock, id_producto),
        )
        conn.commit()
        conn.close()
