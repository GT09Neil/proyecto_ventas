from datetime import date
from typing import List, Optional

from db_connection import get_connection
from modelos.cuota import Cuota


class CuotaDAO:
    @staticmethod
    def listar_todas() -> List[Cuota]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_cuota, id_credito, numero, fecha_programada, valor_programado,
                   valor_pagado, fecha_pago, estado
            FROM Cuota
            ORDER BY id_credito, numero
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [Cuota(*row) for row in rows]

    @staticmethod
    def listar_por_credito(id_credito: int) -> List[Cuota]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_cuota, id_credito, numero, fecha_programada, valor_programado,
                   valor_pagado, fecha_pago, estado
            FROM Cuota
            WHERE id_credito = ?
            ORDER BY numero
            """,
            (id_credito,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [Cuota(*row) for row in rows]

    @staticmethod
    def obtener_por_id(id_cuota: int) -> Optional[Cuota]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_cuota, id_credito, numero, fecha_programada, valor_programado,
                   valor_pagado, fecha_pago, estado
            FROM Cuota
            WHERE id_cuota = ?
            """,
            (id_cuota,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Cuota(*row)

    @staticmethod
    def crear(cuota: Cuota) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Cuota (id_credito, numero, fecha_programada, valor_programado,
                               valor_pagado, fecha_pago, estado)
            OUTPUT INSERTED.id_cuota
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cuota.id_credito,
                cuota.numero,
                cuota.fecha_programada,
                cuota.valor_programado,
                cuota.valor_pagado,
                cuota.fecha_pago,
                cuota.estado,
            ),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return nuevo_id

    @staticmethod
    def actualizar(cuota: Cuota) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Cuota
            SET id_credito = ?, numero = ?, fecha_programada = ?, valor_programado = ?,
                valor_pagado = ?, fecha_pago = ?, estado = ?
            WHERE id_cuota = ?
            """,
            (
                cuota.id_credito,
                cuota.numero,
                cuota.fecha_programada,
                cuota.valor_programado,
                cuota.valor_pagado,
                cuota.fecha_pago,
                cuota.estado,
                cuota.id_cuota,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_pago(id_cuota: int, valor_pagado: float, fecha_pago: Optional[date] = None) -> None:
        if fecha_pago is None:
            fecha_pago = date.today()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Cuota
            SET valor_pagado = ?, fecha_pago = ?, estado = 'Pagada'
            WHERE id_cuota = ?
            """,
            (valor_pagado, fecha_pago, id_cuota),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(id_cuota: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cuota WHERE id_cuota = ?", (id_cuota,))
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar_por_credito(id_credito: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cuota WHERE id_credito = ?", (id_credito,))
        conn.commit()
        conn.close()

