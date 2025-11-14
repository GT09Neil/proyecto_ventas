from datetime import date

from PySide6.QtWidgets import (
    QFrame,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.venta_dao import VentaDAO
from dao.cliente_dao import ClienteDAO
from dao.credito_dao import CreditoDAO
from dao.cuota_dao import CuotaDAO


class CuotasController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/Cuotas.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.buscar_btn: QPushButton = self.ui.findChild(QPushButton, "BuscarBTN")
        self.pago_btn: QPushButton = self.ui.findChild(QPushButton, "RegistrarPagoBTN")

        self.id_venta_txt: QLineEdit = self.ui.findChild(QLineEdit, "idVentaTXT")
        self.total_credito_txt: QLineEdit = self.ui.findChild(QLineEdit, "totalCreditoTXT")
        self.saldo_restante_txt: QLineEdit = self.ui.findChild(QLineEdit, "saldoRestanteTXT")

        self.nombre_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreCTXT")
        self.direccion_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "DireccionCTXT")
        self.email_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "EmailCTXT")
        self.telefono_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "TelefonoCTXT")

        self.tabla_cuotas: QTableWidget = self.ui.findChild(QTableWidget, "tablaCuotas")

        self._venta_actual = None
        self._credito_actual = None
        self._cuotas_actuales = []

        self._configurar_tabla()
        self._conectar_eventos()

        self.show()

    def _configurar_tabla(self):
        if not self.tabla_cuotas:
            return
        self.tabla_cuotas.setColumnCount(5)
        self.tabla_cuotas.setHorizontalHeaderLabels(
            ["Número", "Fecha Programada", "Valor", "Estado", "Fecha Pago"]
        )
        self.tabla_cuotas.setAlternatingRowColors(True)
        self.tabla_cuotas.setSortingEnabled(True)

    def _conectar_eventos(self):
        if self.buscar_btn:
            self.buscar_btn.clicked.connect(self._buscar_credito)
        if self.pago_btn:
            self.pago_btn.clicked.connect(self._registrar_pago)

    def _buscar_credito(self):
        if not self.id_venta_txt:
            return
        texto = self.id_venta_txt.text().strip()
        if not texto:
            QMessageBox.warning(self, "Dato requerido", "Ingrese el número de venta.")
            return
        try:
            id_venta = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Dato inválido", "El número de venta debe ser numérico.")
            return

        try:
            venta = VentaDAO.obtener_por_id(id_venta)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo buscar la venta:\n{error}")
            return

        if not venta:
            QMessageBox.information(self, "Sin resultados", "No se encontró una venta con ese número.")
            return

        self._venta_actual = venta

        try:
            credito = CreditoDAO.obtener_por_venta(venta.id_venta)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo obtener el crédito asociado:\n{error}")
            return

        if not credito:
            QMessageBox.information(self, "Sin crédito", "La venta indicada no tiene un crédito registrado.")
            self._mostrar_cuotas([])
            return

        self._credito_actual = credito

        if self.total_credito_txt:
            self.total_credito_txt.setText(f"{venta.total:.2f}")
        if self.saldo_restante_txt:
            self.saldo_restante_txt.setText(f"{credito.saldo:.2f}")

        try:
            cliente = ClienteDAO.obtener_por_id(venta.id_cliente)
        except Exception as error:
            QMessageBox.warning(self, "Advertencia", f"No se pudo leer el cliente:\n{error}")
            cliente = None

        if cliente:
            if self.nombre_cli_txt:
                self.nombre_cli_txt.setText(cliente.nombre)
            if self.direccion_cli_txt:
                self.direccion_cli_txt.setText(cliente.direccion or "")
            if self.email_cli_txt:
                self.email_cli_txt.setText(cliente.email or "")
            if self.telefono_cli_txt:
                self.telefono_cli_txt.setText(cliente.telefono or "")

        try:
            cuotas = CuotaDAO.listar_por_credito(credito.id_credito)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las cuotas:\n{error}")
            cuotas = []
        self._cuotas_actuales = cuotas
        self._mostrar_cuotas(cuotas)

    def _mostrar_cuotas(self, cuotas):
        if not self.tabla_cuotas:
            return
        self.tabla_cuotas.setRowCount(len(cuotas))
        for fila, cuota in enumerate(cuotas):
            datos = [
                str(cuota.numero),
                cuota.fecha_programada.strftime("%Y-%m-%d") if cuota.fecha_programada else "",
                f"{cuota.valor_programado:.2f}",
                cuota.estado,
                cuota.fecha_pago.strftime("%Y-%m-%d") if cuota.fecha_pago else "",
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setData(Qt.UserRole, cuota.id_cuota)
                self.tabla_cuotas.setItem(fila, columna, item)
        self.tabla_cuotas.resizeColumnsToContents()

    def _registrar_pago(self):
        if not self._credito_actual:
            QMessageBox.warning(self, "Sin crédito", "Busque primero un crédito válido.")
            return
        if not self.tabla_cuotas or not self.tabla_cuotas.selectionModel():
            return
        filas = self.tabla_cuotas.selectionModel().selectedRows()
        if not filas:
            QMessageBox.warning(self, "Selección requerida", "Seleccione la cuota que desea marcar como pagada.")
            return

        fila = filas[0].row()
        item = self.tabla_cuotas.item(fila, 0)
        if not item:
            return
        id_cuota = item.data(Qt.UserRole)
        if not id_cuota:
            QMessageBox.warning(self, "Error", "No se pudo determinar la cuota seleccionada.")
            return

        cuota = next((c for c in self._cuotas_actuales if c.id_cuota == id_cuota), None)
        if not cuota:
            QMessageBox.warning(self, "Error", "No se encontró la cuota en memoria.")
            return

        if cuota.estado == "Pagada":
            QMessageBox.information(self, "Información", "La cuota ya está marcada como pagada.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Registrar pago de la cuota {cuota.numero}?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            CuotaDAO.registrar_pago(cuota.id_cuota, cuota.valor_programado, date.today())
            nuevo_saldo = max(self._credito_actual.saldo - cuota.valor_programado, 0)
            nuevo_estado = "Liquidado" if nuevo_saldo <= 0.01 else "Activo"
            CreditoDAO.actualizar_saldo_estado(self._credito_actual.id_credito, nuevo_saldo, nuevo_estado)
            self._credito_actual.saldo = nuevo_saldo
            self._credito_actual.estado = nuevo_estado

            if self.saldo_restante_txt:
                self.saldo_restante_txt.setText(f"{nuevo_saldo:.2f}")

            cuotas = CuotaDAO.listar_por_credito(self._credito_actual.id_credito)
            self._cuotas_actuales = cuotas
            self._mostrar_cuotas(cuotas)
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el pago:\n{error}")