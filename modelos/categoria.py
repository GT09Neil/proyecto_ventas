from db_connection import get_connection
from modelos.categoria import Categoria

class CategoriaDAO:

    @staticmethod
    def listar():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_categoria, nombre, iva, utilidad FROM Categoria")
        rows = cursor.fetchall()
        conn.close()
        return [Categoria(*row) for row in rows]
