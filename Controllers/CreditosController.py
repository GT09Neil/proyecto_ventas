from datetime import datetime

from PySide6.QtWidgets import (
    QFrame,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QComboBox,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.venta_dao import VentaDAO
from dao.cliente_dao import ClienteDAO
from dao.credito_dao import CreditoDAO
from dao.cuota_dao import CuotaDAO
from modelos.credito import Credito
from modelos.cuota import Cuota


class CreditosController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/Creditos.ui")
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
        self.calcular_btn: QPushButton = self.ui.findChild(QPushButton, "CalcularCuotasBTN")
        self.registrar_btn: QPushButton = self.ui.findChild(QPushButton, "RegistrarCreditoBTN")

        self.id_venta_txt: QLineEdit = self.ui.findChild(QLineEdit, "idVentaTXT")
        self.total_venta_txt: QLineEdit = self.ui.findChild(QLineEdit, "totalVentaTXT")
        self.cuota_inicial_txt: QLineEdit = self.ui.findChild(QLineEdit, "CuotaInicialTXT")
        self.saldo_financiar_txt: QLineEdit = self.ui.findChild(QLineEdit, "saldoFinanciarTXT")
        self.numero_cuotas_cmb: QComboBox = self.ui.findChild(QComboBox, "NumeroCuotasCMB")
        self.valor_cuota_txt: QLineEdit = self.ui.findChild(QLineEdit, "valorCuotaTXT")

        self.nombre_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreCTXT")
        self.direccion_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "DireccionCTXT")
        self.email_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "EmailCTXT")
        self.telefono_cli_txt: QLineEdit = self.ui.findChild(QLineEdit, "TelefonoCTXT")

        self.tabla_cuotas: QTableWidget = self.ui.findChild(QTableWidget, "TablaCuotasV")

        # permitir edición de campos necesarios
        if self.cuota_inicial_txt:
            self.cuota_inicial_txt.setReadOnly(False)
        if self.valor_cuota_txt:
            self.valor_cuota_txt.setReadOnly(True)
        if self.saldo_financiar_txt:
            self.saldo_financiar_txt.setReadOnly(True)

        self._venta_actual = None
        self._credito_existente = None
        self._plan_cuotas_cache: list[Cuota] = []

        self._configurar_tabla()
        self._conectar_eventos()

        self.show()

    def _configurar_tabla(self):
        if not self.tabla_cuotas:
            return
        self.tabla_cuotas.setColumnCount(4)
        self.tabla_cuotas.setHorizontalHeaderLabels(
            ["Número", "Fecha Programada", "Valor", "Estado"]
        )
        self.tabla_cuotas.setAlternatingRowColors(True)
        self.tabla_cuotas.setSortingEnabled(False)

    def _conectar_eventos(self):
        if self.buscar_btn:
            self.buscar_btn.clicked.connect(self._buscar_venta)
        if self.calcular_btn:
            self.calcular_btn.clicked.connect(self._calcular_plan)
        if self.registrar_btn:
            self.registrar_btn.clicked.connect(self._registrar_credito)

    def _buscar_venta(self):
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
            QMessageBox.information(self, "Sin resultados", "No existe una venta con ese código.")
            return

        if venta.tipo_pago != "Credito":
            QMessageBox.warning(
                self,
                "Tipo de venta",
                "La venta seleccionada no es a crédito. Ajuste el tipo de pago antes de crear el crédito.",
            )

        self._venta_actual = venta
        self._plan_cuotas_cache = []

        try:
            if CreditoDAO.cliente_tiene_credito_activo(venta.id_cliente, excluir_venta_id=venta.id_venta):
                QMessageBox.warning(
                    self,
                    "Crédito pendiente",
                    "El cliente seleccionado tiene un crédito activo o en mora. "
                    "Debe liquidarlo antes de registrar uno nuevo.",
                )
                self._venta_actual = None
                self._credito_existente = None
                self._mostrar_cuotas([])
                return
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo validar el estado del cliente:\n{error}")
            self._venta_actual = None
            self._credito_existente = None
            self._mostrar_cuotas([])
            return

        if self.total_venta_txt:
            self.total_venta_txt.setText(f"{venta.total:.2f}")

        cuota_inicial = round(venta.total * 0.30, 2)
        saldo_financiar = round(venta.total * 0.70 * 1.05, 2)

        if self.cuota_inicial_txt:
            self.cuota_inicial_txt.setText(f"{cuota_inicial:.2f}")
        if self.valor_cuota_txt:
            self.valor_cuota_txt.clear()
        if self.saldo_financiar_txt:
            self.saldo_financiar_txt.setText(f"{saldo_financiar:.2f}")
        if self.numero_cuotas_cmb:
            self.numero_cuotas_cmb.setCurrentIndex(0)

        # Cargar datos del cliente
        try:
            cliente = ClienteDAO.obtener_por_id(venta.id_cliente)
        except Exception as error:
            QMessageBox.warning(self, "Advertencia", f"No se pudo obtener el cliente:\n{error}")
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
            credito = CreditoDAO.obtener_por_venta(venta.id_venta)
        except Exception as error:
            QMessageBox.warning(self, "Advertencia", f"No se pudo determinar el crédito existente:\n{error}")
            credito = None

        self._credito_existente = credito

        if credito:
            if self.cuota_inicial_txt:
                self.cuota_inicial_txt.setText(f"{credito.cuota_inicial:.2f}")
            if self.saldo_financiar_txt:
                self.saldo_financiar_txt.setText(f"{credito.saldo:.2f}")
            if self.numero_cuotas_cmb:
                index = self.numero_cuotas_cmb.findText(str(credito.meses))
                if index != -1:
                    self.numero_cuotas_cmb.setCurrentIndex(index)
            if self.valor_cuota_txt:
                self.valor_cuota_txt.setText(self._calcular_valor_cuota_texto(credito))

            try:
                cuotas = CuotaDAO.listar_por_credito(credito.id_credito)
            except Exception as error:
                QMessageBox.warning(self, "Advertencia", f"No se pudieron cargar cuotas:\n{error}")
                cuotas = []
            self._mostrar_cuotas(cuotas)
        else:
            self._mostrar_cuotas([])

    def _calcular_valor_cuota_texto(self, credito: Credito) -> str:
        if credito.meses <= 0:
            return "0.00"
        return f"{credito.saldo / credito.meses:.2f}"

    def _calcular_plan(self):
        if not self._venta_actual:
            QMessageBox.warning(self, "Sin venta", "Busque primero la venta a financiar.")
            return

        if not self.numero_cuotas_cmb or self.numero_cuotas_cmb.currentText() == "":
            QMessageBox.warning(self, "Dato requerido", "Seleccione el número de cuotas.")
            return

        try:
            meses = int(self.numero_cuotas_cmb.currentText())
        except ValueError:
            QMessageBox.warning(self, "Dato inválido", "Número de cuotas no válido.")
            return

        try:
            saldo = float(self.saldo_financiar_txt.text().strip() or 0)
        except ValueError:
            QMessageBox.warning(self, "Dato inválido", "El saldo a financiar no es válido.")
            return

        if saldo <= 0:
            QMessageBox.warning(self, "Dato inválido", "El saldo a financiar debe ser mayor que cero.")
            return

        valor_cuota = saldo / meses if meses else 0

        if self.valor_cuota_txt:
            self.valor_cuota_txt.setText(f"{valor_cuota:.2f}")

        self._plan_cuotas_cache = self._generar_cuotas_temporales(meses, saldo)
        self._mostrar_cuotas(self._plan_cuotas_cache)

    def _generar_cuotas_temporales(self, meses: int, monto_total: float) -> list[Cuota]:
        cuotas = []
        fecha_base = self._venta_actual.fecha or datetime.now()
        if meses <= 0:
            return cuotas
        cuota_base = round(monto_total / meses, 2)
        acumulado = 0.0
        for i in range(1, meses + 1):
            fecha_programada = self._sumar_meses(fecha_base, i)
            valor_programado = cuota_base
            if i == meses:
                valor_programado = round(monto_total - acumulado, 2)
            acumulado += valor_programado
            cuotas.append(
                Cuota(
                    id_credito=None,
                    numero=i,
                    fecha_programada=fecha_programada.date(),
                    valor_programado=valor_programado,
                    valor_pagado=0.0,
                    fecha_pago=None,
                    estado="Pendiente",
                )
            )
        return cuotas

    @staticmethod
    def _sumar_meses(fecha: datetime, meses: int) -> datetime:
        anio = fecha.year + (fecha.month - 1 + meses) // 12
        mes = (fecha.month - 1 + meses) % 12 + 1
        dia = min(fecha.day, _dias_en_mes(anio, mes))
        return datetime(anio, mes, dia, fecha.hour, fecha.minute, fecha.second)

    def _mostrar_cuotas(self, cuotas: list[Cuota]):
        if not self.tabla_cuotas:
            return
        self.tabla_cuotas.setRowCount(len(cuotas))
        for fila, cuota in enumerate(cuotas):
            datos = [
                str(cuota.numero),
                cuota.fecha_programada.strftime("%Y-%m-%d") if cuota.fecha_programada else "",
                f"{cuota.valor_programado:.2f}",
                cuota.estado,
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_cuotas.setItem(fila, columna, item)
        self.tabla_cuotas.resizeColumnsToContents()

    def _registrar_credito(self):
        if not self._venta_actual:
            QMessageBox.warning(self, "Sin venta", "Debe buscar la venta antes de registrar el crédito.")
            return

        if self._credito_existente:
            QMessageBox.information(
                self,
                "Crédito existente",
                "Esta venta ya tiene un crédito registrado. Puede gestionarlo desde la pestaña de cuotas.",
            )
            return

        if not self._plan_cuotas_cache:
            QMessageBox.warning(self, "Plan pendiente", "Calcule primero el plan de cuotas.")
            return

        try:
            cuota_inicial = float(self.cuota_inicial_txt.text().strip() or 0)
            saldo = float(self.saldo_financiar_txt.text().strip() or 0)
            meses = int(self.numero_cuotas_cmb.currentText())
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "Revise los valores numéricos del crédito.")
            return

        if saldo <= 0:
            QMessageBox.warning(self, "Datos inválidos", "El saldo a financiar debe ser mayor que cero.")
            return

        credito = Credito(
            id_credito=None,
            id_venta=self._venta_actual.id_venta,
            cuota_inicial=cuota_inicial,
            saldo=saldo,
            meses=meses,
            interes=0.05,
            estado="Activo",
        )

        try:
            id_credito = CreditoDAO.crear(credito)
            for cuota in self._plan_cuotas_cache:
                cuota.id_credito = id_credito
                CuotaDAO.crear(cuota)

            self._credito_existente = CreditoDAO.obtener_por_id(id_credito)
            cuotas_guardadas = CuotaDAO.listar_por_credito(id_credito)
            self._mostrar_cuotas(cuotas_guardadas)
            QMessageBox.information(self, "Éxito", "Crédito registrado y plan de cuotas generado.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el crédito:\n{error}")


def _dias_en_mes(anio: int, mes: int) -> int:
    if mes in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if mes in (4, 6, 9, 11):
        return 30
    # febrero
    bisiesto = (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)
    return 29 if bisiesto else 28