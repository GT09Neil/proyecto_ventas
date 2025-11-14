from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class FacturaDialog(QDialog):
    def __init__(self, datos_factura: dict, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog)
        self._datos = datos_factura
        venta = datos_factura.get("venta", {})
        numero = venta.get("id_venta", "N/D")
        self.setWindowTitle(f"Factura de venta #{numero}")
        self.setMinimumWidth(720)

        self._tabla_detalle: QTableWidget | None = None
        self._summary_label: QLabel | None = None

        self._construir_ui()

    # ------------------------------------------------------------------ UI --
    def _construir_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QLabel(self._generar_encabezado_html())
        header.setTextFormat(Qt.TextFormat.RichText)
        header.setWordWrap(True)
        layout.addWidget(header)

        self._tabla_detalle = self._crear_tabla_detalle()
        layout.addWidget(self._tabla_detalle)

        self._summary_label = QLabel(self._generar_resumen_html())
        self._summary_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self._summary_label)

        botones_layout = QHBoxLayout()
        exportar_btn = QPushButton("Exportar a PDF", self)
        exportar_btn.clicked.connect(self._exportar_pdf)
        cerrar_btn = QPushButton("Cerrar", self)
        cerrar_btn.clicked.connect(self.close)

        botones_layout.addStretch()
        botones_layout.addWidget(exportar_btn)
        botones_layout.addWidget(cerrar_btn)

        layout.addLayout(botones_layout)

    def _crear_tabla_detalle(self) -> QTableWidget:
        detalles = self._datos.get("detalles", [])
        columnas = ["Código", "Producto", "Categoría", "Cantidad", "Precio unitario", "IVA", "Total"]

        tabla = QTableWidget(len(detalles), len(columnas), self)
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        for fila, item in enumerate(detalles):
            valores = [
                item.get("codigo", ""),
                item.get("producto", ""),
                item.get("categoria", ""),
                f"{item.get('cantidad', 0):.0f}",
                f"$ {item.get('precio_unitario', 0):.2f}",
                f"$ {item.get('iva_valor', 0):.2f}",
                f"$ {item.get('total_linea', 0):.2f}",
            ]
            for columna, valor in enumerate(valores):
                celda = QTableWidgetItem(valor)
                celda.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla.setItem(fila, columna, celda)

        tabla.resizeColumnsToContents()
        tabla.horizontalHeader().setStretchLastSection(True)
        return tabla

    # ------------------------------------------------------------- Helpers --
    def _generar_encabezado_html(self) -> str:
        venta = self._datos.get("venta", {})
        cliente = self._datos.get("cliente", {})
        usuario = self._datos.get("usuario", {})

        fecha = venta.get("fecha", "N/D")
        tipo = venta.get("tipo", "N/D")

        vendedor = usuario.get("nombre", "N/D")
        vendedor_id = usuario.get("cedula", "N/D")

        cliente_info = (
            f"<b>{cliente.get('nombre', 'N/D')}</b><br>"
            f"Cédula: {cliente.get('cedula', 'N/D')}<br>"
            f"Dirección: {cliente.get('direccion', 'N/D')}<br>"
            f"Email: {cliente.get('email', 'N/D')} | Tel: {cliente.get('telefono', 'N/D')}"
        )

        vendedor_info = f"{vendedor} ({vendedor_id})"

        return f"""
        <h2 style='text-align:center;'>Factura de venta #{venta.get('id_venta', 'N/D')}</h2>
        <p>
            <b>Fecha:</b> {fecha} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Tipo de venta:</b> {tipo} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Vendedor:</b> {vendedor_info}
        </p>
        <p>
            <b>Cliente:</b><br>
            {cliente_info}
        </p>
        """

    def _generar_resumen_html(self) -> str:
        totales = self._datos.get("totales", {})
        subtotal = totales.get("subtotal", 0.0)
        iva = totales.get("iva", 0.0)
        total = totales.get("total", 0.0)
        total_registrado = totales.get("total_registrado", total)

        diferencia = abs(total - total_registrado)
        nota_total = ""
        if diferencia >= 0.01:
            nota_total = (
                "<br><i>Nota: El total calculado difiere del total registrado en la venta. "
                "Revise la configuración de impuestos.</i>"
            )

        return (
            "<h3>Resumen</h3>"
            f"<p><b>Subtotal:</b> $ {subtotal:.2f}<br>"
            f"<b>IVA generado:</b> $ {iva:.2f}<br>"
            f"<b>Total con IVA:</b> $ {total:.2f}<br>"
            f"<b>Total registrado en venta:</b> $ {total_registrado:.2f}"
            f"{nota_total}</p>"
        )

    def _generar_html_factura(self) -> str:
        encabezado = self._generar_encabezado_html()
        totales = self._generar_resumen_html()

        filas_html = ""
        for item in self._datos.get("detalles", []):
            filas_html += (
                "<tr>"
                f"<td>{item.get('codigo', '')}</td>"
                f"<td>{item.get('producto', '')}</td>"
                f"<td>{item.get('categoria', '')}</td>"
                f"<td style='text-align:right;'>{item.get('cantidad', 0):.0f}</td>"
                f"<td style='text-align:right;'>$ {item.get('precio_unitario', 0):.2f}</td>"
                f"<td style='text-align:right;'>$ {item.get('iva_valor', 0):.2f}</td>"
                f"<td style='text-align:right;'>$ {item.get('total_linea', 0):.2f}</td>"
                "</tr>"
            )

        tabla_html = f"""
        <table border='1' cellspacing='0' cellpadding='4' width='100%'>
            <thead style='background-color:#f0f0f0;'>
                <tr>
                    <th>Código</th>
                    <th>Producto</th>
                    <th>Categoría</th>
                    <th>Cantidad</th>
                    <th>Precio unitario</th>
                    <th>IVA</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>
        """

        return f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{font-family: Arial, Helvetica, sans-serif; font-size: 12px;}}
                h2, h3 {{text-align: center;}}
                table {{border-collapse: collapse; margin-top: 12px;}}
            </style>
        </head>
        <body>
            {encabezado}
            {tabla_html}
            {totales}
        </body>
        </html>
        """

    # --------------------------------------------------------------- Slots --
    def _exportar_pdf(self) -> None:
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar factura como PDF",
            f"factura_{self._datos.get('venta', {}).get('id_venta', '')}.pdf",
            "Archivos PDF (*.pdf)",
        )
        if not ruta:
            return

        try:
            html = self._generar_html_factura()
            documento = QTextDocument()
            documento.setHtml(html)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(ruta)
            documento.print(printer)
            QMessageBox.information(self, "Factura", "Factura exportada correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo exportar la factura:\n{error}")


