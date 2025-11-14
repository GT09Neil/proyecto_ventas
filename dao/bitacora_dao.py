from typing import Optional

from db_connection import get_connection


class BitacoraDAO:
    @staticmethod
    def registrar(id_usuario: int, tipo_evento: str, detalle: Optional[str] = None) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Bitacora (id_usuario, tipo_evento, detalle)
            VALUES (?, ?, ?)
            """,
            (id_usuario, tipo_evento, detalle),
        )
        conn.commit()
        conn.close()


    @staticmethod
    def listar(limit: int = 200):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT TOP ({limit})
                   b.id_bitacora,
                   b.fecha_hora,
                   b.tipo_evento,
                   ISNULL(b.detalle, '') AS detalle,
                   u.id_usuario,
                   u.nombre,
                   u.cedula,
                   u.rol
            FROM Bitacora b
            INNER JOIN Usuario u ON u.id_usuario = b.id_usuario
            ORDER BY b.fecha_hora DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

