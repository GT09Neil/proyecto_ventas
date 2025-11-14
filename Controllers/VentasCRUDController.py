from datetime import datetime

from PySide6.QtWidgets import (
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QPushButton,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.venta_dao import VentaDAO
from dao.detalle_venta_dao import DetalleVentaDAO
from dao.credito_dao import CreditoDAO
from dao.cuota_dao import CuotaDAO
from modelos.venta import Venta


class VentasCRUDController(QFrame):
    def __init__(self, usuario_actual=None):
        super().__init__()
        self.usuario_actual = usuario_actual

        loader = QUiLoader()
        file = QFile("GUI/VentasCRUD.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.tabla: QTableWidget = self.ui.findChild(QTableWidget, "TablaVentas")
        self.id_txt: QLineEdit = self.ui.findChild(QLineEdit, "idVentaTXT")
        self.id_cliente_txt: QLineEdit = self.ui.findChild(QLineEdit, "idClienteTXT")
        self.tipo_pago_txt: QLineEdit = self.ui.findChild(QLineEdit, "TipoPagoTXT")
        self.fecha_txt: QLineEdit = self.ui.findChild(QLineEdit, "fechaVentaTXT")
        self.total_txt: QLineEdit = self.ui.findChild(QLineEdit, "TotalVentaTXT")

        self.agregar_btn: QPushButton = self.ui.findChild(QPushButton, "AgregarBTN")
        self.actualizar_btn: QPushButton = self.ui.findChild(QPushButton, "ActualizarBTN")
        self.eliminar_btn: QPushButton = self.ui.findChild(QPushButton, "EliminarBTN")

        self._venta_en_edicion: Venta | None = None

        self._configurar_tabla()
        self._conectar_eventos()
        self.cargar_ventas()

        self.show()

    def _configurar_tabla(self):
        if not self.tabla:
            return
        self.tabla.setSortingEnabled(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.itemSelectionChanged.connect(self._al_seleccionar_fila)

    def _conectar_eventos(self):
        if self.agregar_btn:
            self.agregar_btn.clicked.connect(self._agregar_venta)
        if self.actualizar_btn:
            self.actualizar_btn.clicked.connect(self._actualizar_venta)
        if self.eliminar_btn:
            self.eliminar_btn.clicked.connect(self._eliminar_venta)

    def cargar_ventas(self):
        if not self.tabla:
            return
        try:
            ventas = VentaDAO.listar()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las ventas:\n{error}")
            return

        self.tabla.setRowCount(len(ventas))
        for fila, venta in enumerate(ventas):
            datos = [
                str(venta.id_venta),
                str(venta.id_cliente),
                venta.tipo_pago,
                venta.fecha.strftime("%Y-%m-%d %H:%M") if venta.fecha else "",
                f"{venta.total:.2f}",
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor if valor is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def _parsear_fecha(self, texto: str):
        if not texto:
            return datetime.now()
        formatos = ["%Y-%m-%d", "%Y-%m-%d %H:%M", "%d/%m/%Y", "%d/%m/%Y %H:%M"]
        for formato in formatos:
            try:
                return datetime.strptime(texto, formato)
            except ValueError:
                continue
        raise ValueError("Formato de fecha inválido.")

    def _obtener_datos_formulario(self) -> Venta | None:
        id_cliente_texto = self.id_cliente_txt.text().strip() if self.id_cliente_txt else ""
        tipo_pago = self.tipo_pago_txt.text().strip().capitalize() if self.tipo_pago_txt else ""
        fecha_texto = self.fecha_txt.text().strip() if self.fecha_txt else ""
        total_texto = self.total_txt.text().strip() if self.total_txt else "0"

        if not id_cliente_texto or not tipo_pago:
            QMessageBox.warning(self, "Campos requeridos", "Cliente y tipo de pago son obligatorios.")
            return None

        try:
            id_cliente = int(id_cliente_texto)
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "El cliente debe ser numérico.")
            return None

        if tipo_pago not in ["Contado", "Credito", "Crédito"]:
            QMessageBox.warning(self, "Datos inválidos", "El tipo de pago debe ser Contado o Crédito.")
            return None

        try:
            fecha = self._parsear_fecha(fecha_texto)
        except ValueError as error:
            QMessageBox.warning(self, "Datos inválidos", str(error))
            return None

        try:
            total = float(total_texto)
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "Ingrese un valor numérico para el total.")
            return None

        tipo_pago_normalizado = "Credito" if tipo_pago.startswith("Cr") else "Contado"

        venta = Venta(
            id_venta=self._venta_en_edicion.id_venta if self._venta_en_edicion else None,
            id_cliente=id_cliente,
            fecha=fecha,
            tipo_pago=tipo_pago_normalizado,
            total=total,
            id_usuario=self._venta_en_edicion.id_usuario if self._venta_en_edicion else getattr(self.usuario_actual, "id_usuario", None),
            estado=self._venta_en_edicion.estado if self._venta_en_edicion else "Registrada",
        )

        if venta.id_usuario is None:
            QMessageBox.warning(self, "Usuario requerido", "No se pudo determinar el usuario que crea la venta.")
            return None

        return venta

    def _agregar_venta(self):
        venta = self._obtener_datos_formulario()
        if venta is None:
            return

        try:
            nuevo_id = VentaDAO.agregar(venta)
            venta.id_venta = nuevo_id
            self.cargar_ventas()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Venta registrada correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo registrar la venta:\n{error}")

    def _actualizar_venta(self):
        if not self._venta_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione una venta.")
            return

        venta = self._obtener_datos_formulario()
        if venta is None:
            return

        venta.id_venta = self._venta_en_edicion.id_venta

        try:
            VentaDAO.actualizar(venta)
            self.cargar_ventas()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Venta actualizada correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la venta:\n{error}")

    def _eliminar_venta(self):
        if not self._venta_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione una venta para eliminarla.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar la venta {self._venta_en_edicion.id_venta}? Se eliminarán los detalles asociados.",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            DetalleVentaDAO.eliminar_por_venta(self._venta_en_edicion.id_venta)
            credito = CreditoDAO.obtener_por_venta(self._venta_en_edicion.id_venta)
            if credito:
                CuotaDAO.eliminar_por_credito(credito.id_credito)
                CreditoDAO.eliminar(credito.id_credito)
            VentaDAO.eliminar(self._venta_en_edicion.id_venta)
            self.cargar_ventas()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Venta eliminada.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la venta:\n{error}")

    def _al_seleccionar_fila(self):
        if not self.tabla or not self.tabla.selectionModel():
            return
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return

        fila = filas[0].row()
        id_venta = int(self.tabla.item(fila, 0).text())
        venta = VentaDAO.obtener_por_id(id_venta)
        if not venta:
            return

        self._venta_en_edicion = venta
        if self.id_txt:
            self.id_txt.setText(str(venta.id_venta))
        if self.id_cliente_txt:
            self.id_cliente_txt.setText(str(venta.id_cliente))
        if self.tipo_pago_txt:
            self.tipo_pago_txt.setText(venta.tipo_pago)
        if self.fecha_txt:
            if venta.fecha:
                self.fecha_txt.setText(venta.fecha.strftime("%Y-%m-%d %H:%M"))
            else:
                self.fecha_txt.clear()
        if self.total_txt:
            self.total_txt.setText(f"{venta.total:.2f}")

    def _limpiar_formulario(self):
        self._venta_en_edicion = None
        for widget in [self.id_txt, self.id_cliente_txt, self.tipo_pago_txt, self.fecha_txt, self.total_txt]:
            if widget:
                widget.clear()
        if self.tabla:
            self.tabla.clearSelection()