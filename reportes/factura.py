from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List

from db_connection import get_connection


def _normalizar(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")
    return valor


def generar_datos_factura(id_venta: int) -> Dict[str, Any]:
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                v.id_venta,
                v.fecha,
                v.tipo,
                v.total,
                v.estado,
                cli.nombre AS cliente_nombre,
                cli.cedula AS cliente_cedula,
                cli.direccion AS cliente_direccion,
                cli.telefono AS cliente_telefono,
                cli.correo AS cliente_email,
                u.nombre AS usuario_nombre,
                u.cedula AS usuario_cedula
            FROM Venta v
            INNER JOIN Cliente cli ON cli.id_cliente = v.id_cliente
            LEFT JOIN Usuario u ON u.id_usuario = v.id_usuario
            WHERE v.id_venta = ?
            """,
            (id_venta,),
        )
        venta_row = cursor.fetchone()
        if not venta_row:
            raise ValueError(f"No existe la venta #{id_venta}.")

        cursor.execute(
            """
            SELECT
                p.codigo,
                p.nombre AS producto,
                cat.nombre AS categoria,
                ISNULL(cat.iva, 0) AS iva,
                dv.cantidad,
                dv.precio_unitario,
                dv.subtotal
            FROM DetalleVenta dv
            INNER JOIN Producto p ON p.id_producto = dv.id_producto
            INNER JOIN Categoria cat ON cat.id_categoria = p.id_categoria
            WHERE dv.id_venta = ?
            ORDER BY dv.id_detalle
            """,
            (id_venta,),
        )

        subtotal = 0.0
        iva_total = 0.0
        detalles: List[Dict[str, Any]] = []
        for row in cursor.fetchall():
            base = float(row.subtotal or 0.0)
            iva_tarifa = float(row.iva or 0.0)
            iva_valor = round(base * iva_tarifa, 2)
            total_linea = round(base + iva_valor, 2)

            detalles.append(
                {
                    "codigo": row.codigo,
                    "producto": row.producto,
                    "categoria": row.categoria,
                    "cantidad": float(row.cantidad or 0),
                    "precio_unitario": float(row.precio_unitario or 0.0),
                    "subtotal": base,
                    "iva_tarifa": iva_tarifa,
                    "iva_valor": iva_valor,
                    "total_linea": total_linea,
                }
            )
            subtotal += base
            iva_total += iva_valor

        venta_total = float(venta_row.total or 0.0)
        datos = {
            "venta": {
                "id_venta": venta_row.id_venta,
                "fecha": _normalizar(venta_row.fecha),
                "tipo": venta_row.tipo,
                "total": venta_total,
                "estado": venta_row.estado,
            },
            "cliente": {
                "nombre": venta_row.cliente_nombre,
                "cedula": venta_row.cliente_cedula,
                "direccion": venta_row.cliente_direccion,
                "telefono": venta_row.cliente_telefono,
                "email": venta_row.cliente_email,
            },
            "usuario": {
                "nombre": venta_row.usuario_nombre or "N/D",
                "cedula": venta_row.usuario_cedula or "N/D",
            },
            "detalles": detalles,
            "totales": {
                "subtotal": round(subtotal, 2),
                "iva": round(iva_total, 2),
                "total": round(subtotal + iva_total, 2),
                "total_registrado": round(venta_total, 2),
            },
        }
        return datos
    finally:
        conn.close()


