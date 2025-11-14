from typing import List, Optional

from db_connection import get_connection
from modelos.credito import Credito


class CreditoDAO:
    @staticmethod
    def listar() -> List[Credito]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_credito, id_venta, cuota_inicial, saldo, meses, interes, estado
            FROM Credito
            ORDER BY id_credito DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            Credito(
                id_credito=row.id_credito,
                id_venta=row.id_venta,
                cuota_inicial=float(row.cuota_inicial or 0),
                saldo=float(row.saldo or 0),
                meses=row.meses,
                interes=float(row.interes or 0),
                estado=row.estado,
            )
            for row in rows
        ]

    @staticmethod
    def obtener_por_id(id_credito: int) -> Optional[Credito]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_credito, id_venta, cuota_inicial, saldo, meses, interes, estado
            FROM Credito
            WHERE id_credito = ?
            """,
            (id_credito,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Credito(
            id_credito=row.id_credito,
            id_venta=row.id_venta,
            cuota_inicial=float(row.cuota_inicial or 0),
            saldo=float(row.saldo or 0),
            meses=row.meses,
            interes=float(row.interes or 0),
            estado=row.estado,
        )

    @staticmethod
    def obtener_por_venta(id_venta: int) -> Optional[Credito]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_credito, id_venta, cuota_inicial, saldo, meses, interes, estado
            FROM Credito
            WHERE id_venta = ?
            """,
            (id_venta,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Credito(
            id_credito=row.id_credito,
            id_venta=row.id_venta,
            cuota_inicial=float(row.cuota_inicial or 0),
            saldo=float(row.saldo or 0),
            meses=row.meses,
            interes=float(row.interes or 0),
            estado=row.estado,
        )

    @staticmethod
    def cliente_tiene_credito_activo(id_cliente: int, excluir_venta_id: Optional[int] = None) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        if excluir_venta_id is None:
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM Credito c
                INNER JOIN Venta v ON v.id_venta = c.id_venta
                WHERE v.id_cliente = ? AND c.estado <> 'Liquidado'
                """,
                (id_cliente,),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM Credito c
                INNER JOIN Venta v ON v.id_venta = c.id_venta
                WHERE v.id_cliente = ? AND c.estado <> 'Liquidado' AND v.id_venta <> ?
                """,
                (id_cliente, excluir_venta_id),
            )
        total = cursor.fetchone()[0]
        conn.close()
        return total > 0

    @staticmethod
    def crear(credito: Credito) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Credito (id_venta, cuota_inicial, saldo, meses, interes, estado)
            OUTPUT INSERTED.id_credito
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                credito.id_venta,
                credito.cuota_inicial,
                credito.saldo,
                credito.meses,
                credito.interes,
                credito.estado,
            ),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return nuevo_id

    @staticmethod
    def actualizar(credito: Credito) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Credito
            SET id_venta = ?, cuota_inicial = ?, saldo = ?, meses = ?, interes = ?, estado = ?
            WHERE id_credito = ?
            """,
            (
                credito.id_venta,
                credito.cuota_inicial,
                credito.saldo,
                credito.meses,
                credito.interes,
                credito.estado,
                credito.id_credito,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def actualizar_saldo_estado(id_credito: int, saldo: float, estado: Optional[str] = None) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        if estado is None:
            cursor.execute(
                "UPDATE Credito SET saldo = ? WHERE id_credito = ?",
                (saldo, id_credito),
            )
        else:
            cursor.execute(
                "UPDATE Credito SET saldo = ?, estado = ? WHERE id_credito = ?",
                (saldo, estado, id_credito),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(id_credito: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Credito WHERE id_credito = ?", (id_credito,))
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar_por_venta(id_venta: int) -> None:
        credito = CreditoDAO.obtener_por_venta(id_venta)
        if not credito:
            return
        CreditoDAO.eliminar(credito.id_credito)

