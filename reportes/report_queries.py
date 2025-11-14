from datetime import datetime, date
from decimal import Decimal
from typing import Iterable, List, Tuple

from db_connection import get_connection


def _ejecutar_consulta(sql: str, parametros: Iterable = ()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(parametros))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description] if cursor.description else []
    conn.close()
    datos = [tuple(_normalizar(valor) for valor in row) for row in rows]
    return columns, datos


def _normalizar(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")
    return valor


def reporte_total_ventas_por_mes(mes: int):
    sql = """
        SELECT
            YEAR(v.fecha) AS Anio,
            DATENAME(month, v.fecha) AS Mes,
            COUNT(DISTINCT v.id_venta) AS NumeroVentas,
            SUM(v.total) AS TotalVentas,
            SUM(CASE WHEN v.tipo = 'Credito' THEN v.total ELSE 0 END) AS TotalCredito,
            SUM(CASE WHEN v.tipo = 'Contado' THEN v.total ELSE 0 END) AS TotalContado,
            SUM(d.cantidad) AS UnidadesVendidas
        FROM Venta v
        INNER JOIN DetalleVenta d ON d.id_venta = v.id_venta
        WHERE MONTH(v.fecha) = ?
        GROUP BY YEAR(v.fecha), DATENAME(month, v.fecha), DATEPART(month, v.fecha)
        ORDER BY Anio, DATEPART(month, v.fecha)
    """
    return _ejecutar_consulta(sql, (mes,))


def reporte_clientes_morosos():
    sql = """
        SELECT
            cli.cedula AS Cedula,
            cli.nombre AS Cliente,
            v.id_venta AS NumeroVenta,
            c.id_credito AS CodigoCredito,
            COUNT(*) AS CuotasEnMora,
            SUM(cu.valor_programado - cu.valor_pagado) AS ValorPendiente,
            MAX(cu.fecha_programada) AS UltimaFechaProgramada
        FROM Credito c
        INNER JOIN Venta v ON v.id_venta = c.id_venta
        INNER JOIN Cliente cli ON cli.id_cliente = v.id_cliente
        INNER JOIN Cuota cu ON cu.id_credito = c.id_credito
        WHERE c.estado <> 'Liquidado'
          AND cu.estado <> 'Pagada'
          AND cu.fecha_programada < CAST(GETDATE() AS DATE)
        GROUP BY cli.cedula, cli.nombre, v.id_venta, c.id_credito
        HAVING SUM(cu.valor_programado - cu.valor_pagado) > 0
        ORDER BY ValorPendiente DESC
    """
    return _ejecutar_consulta(sql)


def reporte_inventario_por_categoria(id_categoria: int):
    sql = """
        SELECT
            c.nombre AS Categoria,
            COUNT(p.id_producto) AS Productos,
            SUM(ISNULL(p.stock,0)) AS StockTotal,
            SUM(ISNULL(p.stock,0) * ISNULL(p.valor_venta,0)) AS ValorVentaEstimado,
            AVG(ISNULL(p.valor_venta,0)) AS PrecioPromedio
        FROM Producto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
        WHERE p.id_categoria = ?
        GROUP BY c.nombre
    """
    return _ejecutar_consulta(sql, (id_categoria,))


def reporte_ventas_periodo(tipo: str, fecha_inicio: date, fecha_fin: date):
    sql = """
        SELECT
            v.tipo AS TipoVenta,
            COUNT(DISTINCT v.id_venta) AS NumeroVentas,
            SUM(ISNULL(v.total,0)) AS TotalVentas,
            SUM(ISNULL(d.cantidad,0)) AS UnidadesVendidas
        FROM Venta v
        LEFT JOIN DetalleVenta d ON d.id_venta = v.id_venta
        WHERE v.fecha BETWEEN ? AND ?
          AND ( ? = 'Todos' OR v.tipo = ? )
        GROUP BY v.tipo
    """
    params = (
        fecha_inicio,
        fecha_fin,
        tipo,
        tipo,
    )
    columnas, filas = _ejecutar_consulta(sql, params)
    columnas = ["TipoVenta", "NumeroVentas", "TotalVentas", "UnidadesVendidas"]
    if not filas:
        return columnas, filas

    normalizados: List[Tuple] = []
    for tipo_venta, numero, total, unidades in filas:
        etiqueta = "Crédito" if str(tipo_venta).lower().startswith("cred") else "Contado"
        normalizados.append(
            (
                etiqueta,
                int(numero or 0),
                round(float(total or 0.0), 2),
                int(unidades or 0),
            )
        )

    if tipo == "Todos" or len(normalizados) > 1:
        total_filas = (
            "Total",
            sum(row[1] for row in normalizados),
            round(sum(row[2] for row in normalizados), 2),
            sum(row[3] for row in normalizados),
        )
        normalizados.append(total_filas)

    return columnas, normalizados


def reporte_iva_trimestral(anio: int, trimestre: int):
    sql = """
        SELECT
            YEAR(v.fecha) AS Anio,
            DATEPART(quarter, v.fecha) AS Trimestre,
            cat.nombre AS Categoria,
            SUM(ISNULL(d.subtotal,0)) AS VentasSinIVA,
            SUM(ISNULL(d.subtotal,0) * ISNULL(cat.iva,0)) AS IvaGenerado,
            SUM(ISNULL(d.subtotal,0) * (1 + ISNULL(cat.iva,0))) AS TotalConIVA
        FROM Venta v
        INNER JOIN DetalleVenta d ON d.id_venta = v.id_venta
        INNER JOIN Producto p ON p.id_producto = d.id_producto
        INNER JOIN Categoria cat ON cat.id_categoria = p.id_categoria
        WHERE YEAR(v.fecha) = ?
          AND DATEPART(quarter, v.fecha) = ?
        GROUP BY YEAR(v.fecha), DATEPART(quarter, v.fecha), cat.nombre
        ORDER BY cat.nombre
    """
    columnas, filas = _ejecutar_consulta(sql, (anio, trimestre))
    columnas = ["Año", "Trimestre", "Categoría", "Ventas sin IVA", "IVA generado", "Total con IVA"]
    if not filas:
        return columnas, filas

    procesados: List[Tuple] = []
    total_base = 0.0
    total_iva = 0.0
    total_general = 0.0

    for anio_val, trimestre_val, categoria, base, iva, total in filas:
        base = float(base or 0.0)
        iva = float(iva or 0.0)
        total = float(total or 0.0)
        procesados.append(
            (
                int(anio_val or anio),
                int(trimestre_val or trimestre),
                categoria,
                round(base, 2),
                round(iva, 2),
                round(total, 2),
            )
        )
        total_base += base
        total_iva += iva
        total_general += total

    procesados.append(
        (
            anio,
            trimestre,
            "TOTAL TRIMESTRE",
            round(total_base, 2),
            round(total_iva, 2),
            round(total_general, 2),
        )
    )

    return columnas, procesados


def reporte_top_clientes(limit: int = 5):
    sql = f"""
        SELECT TOP ({limit})
            cli.cedula AS Cedula,
            cli.nombre AS Cliente,
            COUNT(DISTINCT v.id_venta) AS NumeroVentas,
            SUM(v.total) AS TotalComprado,
            SUM(ISNULL(d.cantidad,0)) AS UnidadesCompradas
        FROM Cliente cli
        INNER JOIN Venta v ON v.id_cliente = cli.id_cliente
        LEFT JOIN DetalleVenta d ON d.id_venta = v.id_venta
        GROUP BY cli.cedula, cli.nombre
        ORDER BY TotalComprado DESC
    """
    return _ejecutar_consulta(sql)


def consulta_ventas_por_cliente(cedula: str):
    sql = """
        SELECT
            v.id_venta AS NumeroVenta,
            v.fecha AS Fecha,
            v.tipo AS TipoVenta,
            v.total AS TotalVenta,
            SUM(ISNULL(d.subtotal,0)) AS SubtotalDetalle,
            SUM(ISNULL(d.cantidad,0)) AS ProductosVendidos
        FROM Cliente cli
        INNER JOIN Venta v ON v.id_cliente = cli.id_cliente
        LEFT JOIN DetalleVenta d ON d.id_venta = v.id_venta
        WHERE cli.cedula = ?
        GROUP BY v.id_venta, v.fecha, v.tipo, v.total
        ORDER BY v.fecha DESC
    """
    return _ejecutar_consulta(sql, (cedula,))


def consulta_productos_bajo_stock():
    sql = """
        SELECT
            p.codigo AS Codigo,
            p.nombre AS Producto,
            c.nombre AS Categoria,
            ISNULL(p.stock,0) AS Stock,
            ISNULL(p.stock_minimo,0) AS StockMinimo,
            ISNULL(p.valor_venta,0) AS ValorVenta
        FROM Producto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
        WHERE ISNULL(p.stock,0) <= ISNULL(p.stock_minimo,0)
        ORDER BY ISNULL(p.stock,0), p.nombre
    """
    return _ejecutar_consulta(sql)


def consulta_creditos_activos():
    sql = """
        SELECT
            c.id_credito AS Credito,
            v.id_venta AS Venta,
            cli.nombre AS Cliente,
            c.saldo AS SaldoPendiente,
            c.meses AS NumeroCuotas,
            COUNT(cu.id_cuota) AS CuotasTotales,
            SUM(CASE WHEN cu.estado = 'Pagada' THEN 1 ELSE 0 END) AS CuotasPagadas
        FROM Credito c
        INNER JOIN Venta v ON v.id_venta = c.id_venta
        INNER JOIN Cliente cli ON cli.id_cliente = v.id_cliente
        LEFT JOIN Cuota cu ON cu.id_credito = c.id_credito
        WHERE c.saldo > 0
        GROUP BY c.id_credito, v.id_venta, cli.nombre, c.saldo, c.meses
        ORDER BY c.saldo DESC
    """
    return _ejecutar_consulta(sql)


def consulta_cuotas_vencidas():
    sql = """
        SELECT
            cli.nombre AS Cliente,
            v.id_venta AS Venta,
            c.id_credito AS Credito,
            cu.numero AS NumeroCuota,
            cu.fecha_programada AS FechaProgramada,
            cu.valor_programado AS ValorProgramado,
            cu.valor_pagado AS ValorPagado,
            cu.estado AS Estado
        FROM Cuota cu
        INNER JOIN Credito c ON c.id_credito = cu.id_credito
        INNER JOIN Venta v ON v.id_venta = c.id_venta
        INNER JOIN Cliente cli ON cli.id_cliente = v.id_cliente
        WHERE cu.estado <> 'Pagada'
          AND cu.fecha_programada < CAST(GETDATE() AS DATE)
        ORDER BY cu.fecha_programada
    """
    return _ejecutar_consulta(sql)


def consulta_ventas_por_usuario():
    sql = """
        SELECT
            u.nombre AS Usuario,
            CASE u.rol
                WHEN 1 THEN 'Administrador'
                WHEN 2 THEN 'Paramétrico'
                WHEN 3 THEN 'Esporádico'
                ELSE 'Desconocido'
            END AS Rol,
            COUNT(v.id_venta) AS NumeroVentas,
            SUM(ISNULL(v.total,0)) AS TotalVentas
        FROM Usuario u
        LEFT JOIN Venta v ON v.id_usuario = u.id_usuario
        GROUP BY u.nombre, u.rol
        ORDER BY TotalVentas DESC
    """
    return _ejecutar_consulta(sql)

