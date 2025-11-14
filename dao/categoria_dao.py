from typing import List, Optional

from db_connection import get_connection
from modelos.categoria import Categoria


class CategoriaDAO:
    @staticmethod
    def listar() -> List[Categoria]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_categoria, nombre, iva, utilidad FROM Categoria ORDER BY nombre"
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            Categoria(
                id_categoria=row.id_categoria,
                nombre=row.nombre,
                iva=float(row.iva),
                utilidad=float(row.utilidad),
            )
            for row in rows
        ]

    @staticmethod
    def obtener_por_id(id_categoria: int) -> Optional[Categoria]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_categoria, nombre, iva, utilidad FROM Categoria WHERE id_categoria = ?",
            (id_categoria,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Categoria(
            id_categoria=row.id_categoria,
            nombre=row.nombre,
            iva=float(row.iva),
            utilidad=float(row.utilidad),
        )

    @staticmethod
    def crear(categoria: Categoria) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Categoria (nombre, iva, utilidad)
            OUTPUT INSERTED.id_categoria
            VALUES (?, ?, ?)
            """,
            (categoria.nombre, categoria.iva, categoria.utilidad),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return nuevo_id

    @staticmethod
    def actualizar(categoria: Categoria) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Categoria
            SET nombre = ?, iva = ?, utilidad = ?
            WHERE id_categoria = ?
            """,
            (categoria.nombre, categoria.iva, categoria.utilidad, categoria.id_categoria),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(id_categoria: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Categoria WHERE id_categoria = ?", (id_categoria,))
        conn.commit()
        conn.close()



