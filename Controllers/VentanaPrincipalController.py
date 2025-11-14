from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QWidget,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt, QRect, QDate

from Controllers.ClienteCRUDController import ClienteCRUDController
from Controllers.ProductoCRUDController import ProductoCRUDController
from Controllers.VentasCRUDController import VentasCRUDController
from Controllers.CategoriaCRUDController import CategoriaCRUDController
from Controllers.RegistrarVentaController import RegistrarVentaController
from Controllers.CreditosController import CreditosController
from Controllers.CuotasController import CuotasController
from Controllers.BitacoraController import BitacoraController
from Controllers.UsuarioCRUDController import UsuarioCRUDController
from Controllers.DataTableDialog import DataTableDialog
from Controllers.CalendarioController import CalendarioController

from dao.bitacora_dao import BitacoraDAO
from dao.categoria_dao import CategoriaDAO
from reportes.report_queries import (
    reporte_total_ventas_por_mes,
    reporte_clientes_morosos,
    reporte_inventario_por_categoria,
    reporte_ventas_periodo,
    reporte_top_clientes,
    reporte_iva_trimestral,
    consulta_ventas_por_cliente,
    consulta_productos_bajo_stock,
    consulta_creditos_activos,
    consulta_cuotas_vencidas,
    consulta_ventas_por_usuario,
)


class VentanaPrincipalController(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._logout_registrado = False
        self._abrir_login_al_cerrar = False

        loader = QUiLoader()
        file = QFile("GUI/VentanaPrincipal.ui")
        if not file.open(QFile.ReadOnly):
            raise RuntimeError("No se pudo abrir GUI/VentanaPrincipal.ui")
        try:
            loaded_ui = loader.load(file)
        except RuntimeError as error:
            print(f"Error al cargar VentanaPrincipal.ui: {error}")
            file.close()
            raise
        file.close()

        self.setCentralWidget(loaded_ui.centralWidget())
        self.tabWidget = self.centralWidget().findChild(QTabWidget, "tabWidget")
        self._titulo_base = loaded_ui.windowTitle()
        self.setWindowTitle(self._titulo_base)
        self.resize(loaded_ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.ClienteBTN = self.tabWidget.findChild(QPushButton, "ClienteBTN", Qt.FindChildrenRecursively)
        if self.ClienteBTN:
            self.ClienteBTN.clicked.connect(self.abrir_CRUD_clientes)

        self.ProductoBTN = self.tabWidget.findChild(QPushButton, "ProductoBTN", Qt.FindChildrenRecursively)
        if self.ProductoBTN:
            self.ProductoBTN.clicked.connect(self.abrir_CRUD_productos)

        self.VentaBTN = self.tabWidget.findChild(QPushButton, "VentaBTN")
        if self.VentaBTN:
            self.VentaBTN.clicked.connect(self.abrir_CRUD_ventas)

        self.CategoriaBTN = self.tabWidget.findChild(QPushButton, "CategoriaBTN", Qt.FindChildrenRecursively)
        if self.CategoriaBTN:
            self.CategoriaBTN.clicked.connect(self.abrir_CRUD_categorias)

        self.RegistrarVentaBTN = self.tabWidget.findChild(QPushButton, "RegistrarVentaBTN", Qt.FindChildrenRecursively)
        if self.RegistrarVentaBTN:
            self.RegistrarVentaBTN.clicked.connect(self.abrir_registrar_venta)

        self.CreditoBTN = self.tabWidget.findChild(QPushButton, "CreditoBTN", Qt.FindChildrenRecursively)
        if self.CreditoBTN:
            self.CreditoBTN.clicked.connect(self.abrir_creditos)

        self.AgregarCuotaBTN = self.tabWidget.findChild(QPushButton, "AgregarCuotaBTN", Qt.FindChildrenRecursively)
        if self.AgregarCuotaBTN:
            self.AgregarCuotaBTN.clicked.connect(self.abrir_cuotas)

        self.BitacoraBTN = self.tabWidget.findChild(QPushButton, "BitacoraBTN", Qt.FindChildrenRecursively)
        if self.BitacoraBTN:
            self.BitacoraBTN.clicked.connect(self.abrir_bitacora)

        self.GestionUsuarioBTN = self.tabWidget.findChild(QPushButton, "GestionUsuarioBTN", Qt.FindChildrenRecursively)
        if self.GestionUsuarioBTN:
            self.GestionUsuarioBTN.clicked.connect(self.abrir_CRUD_usuarios)

        self.CalculadoraBTN = self.tabWidget.findChild(QPushButton, "CalculadoraBTN", Qt.FindChildrenRecursively)
        if self.CalculadoraBTN:
            self.CalculadoraBTN.clicked.connect(self.abrir_calculadora)

        self.CalendarioBTN = self.tabWidget.findChild(QPushButton, "CalendarioBTN", Qt.FindChildrenRecursively)
        if self.CalendarioBTN:
            self.CalendarioBTN.clicked.connect(self.abrir_calendario)

        self.CerrarSesionBTN = self.tabWidget.findChild(QPushButton, "CerrarSesionBTN", Qt.FindChildrenRecursively)
        if self.CerrarSesionBTN:
            self.CerrarSesionBTN.clicked.connect(self.cerrar_sesion)

        self.entidades_tab = self.tabWidget.findChild(QWidget, "EntidadesTab", Qt.FindChildrenRecursively)
        self.transacciones_tab = self.tabWidget.findChild(QWidget, "TransaccionesTab", Qt.FindChildrenRecursively)
        self.reportes_tab = self.tabWidget.findChild(QWidget, "ReportesTab", Qt.FindChildrenRecursively)
        self.consultas_tab = self.tabWidget.findChild(QWidget, "ConsultasTab", Qt.FindChildrenRecursively)
        self.utilidades_tab = self.tabWidget.findChild(QWidget, "UtilidadesTab", Qt.FindChildrenRecursively)
        self.ayudas_tab = self.tabWidget.findChild(QWidget, "AyudasTab", Qt.FindChildrenRecursively)

        self._result_windows: list[DataTableDialog] = []
        self._report_buttons: list[QPushButton] = []
        self._consulta_buttons: list[QPushButton] = []

        self._configurar_reportes_y_consultas()
        self._configurar_interfaz_segun_usuario()

        self.show()

    def abrir_CRUD_clientes(self):
        self.cliente_crud = ClienteCRUDController()
        self.cliente_crud.show()

    def abrir_CRUD_productos(self):
        self.producto_crud = ProductoCRUDController()
        self.producto_crud.show()

    def abrir_CRUD_ventas(self):
        self.venta_crud = VentasCRUDController(self.usuario)
        self.venta_crud.show()

    def abrir_CRUD_categorias(self):
        self.categoria_crud = CategoriaCRUDController()
        self.categoria_crud.show()

    def abrir_registrar_venta(self):
        self.registrar_venta = RegistrarVentaController(self.usuario)
        self.registrar_venta.show()

    def abrir_creditos(self):
        self.creditos = CreditosController()
        self.creditos.show()

    def abrir_cuotas(self):
        self.cuotas = CuotasController()
        self.cuotas.show()

    def abrir_bitacora(self):
        self.bitacora = BitacoraController()
        self.bitacora.show()

    def abrir_CRUD_usuarios(self):
        self.usuario_crud = UsuarioCRUDController()
        self.usuario_crud.show()

    def abrir_calculadora(self):
        import os

        os.startfile("calc.exe")

    def abrir_calendario(self):
        self.calendario = CalendarioController()
        self.calendario.show()

    def cerrar_sesion(self):
        self._abrir_login_al_cerrar = True
        self.close()

    def closeEvent(self, event):
        self._registrar_logout()
        super().closeEvent(event)
        if self._abrir_login_al_cerrar:
            from Controllers.LoginController import LoginController

            self._ventana_login = LoginController()

    def _registrar_logout(self):
        if self._logout_registrado or not getattr(self.usuario, "id_usuario", None):
            return
        try:
            BitacoraDAO.registrar(self.usuario.id_usuario, "Logout", "Salida del sistema")
            self._logout_registrado = True
        except Exception as error:
            print(f"No se pudo registrar la salida en bitácora: {error}")

    def _configurar_reportes_y_consultas(self):
        self.TotalVentasBTN = self.tabWidget.findChild(QPushButton, "TotalVentasBTN", Qt.FindChildrenRecursively)
        if self.TotalVentasBTN:
            self.TotalVentasBTN.clicked.connect(self.generar_reporte_total_ventas)
            self._report_buttons.append(self.TotalVentasBTN)

        self.ReporteClientesBTN = self.tabWidget.findChild(QPushButton, "ReporteClientesBTN", Qt.FindChildrenRecursively)
        if self.ReporteClientesBTN:
            self.ReporteClientesBTN.clicked.connect(self.generar_reporte_clientes_morosos)
            self._report_buttons.append(self.ReporteClientesBTN)

        self.InventarioProductosBTN = self.tabWidget.findChild(QPushButton, "InventarioProductosBTN", Qt.FindChildrenRecursively)
        if self.InventarioProductosBTN:
            self.InventarioProductosBTN.clicked.connect(self.generar_reporte_inventario)
            self._report_buttons.append(self.InventarioProductosBTN)

        self.VentasPeriodoBTN = self.tabWidget.findChild(QPushButton, "VentasPeriodoBTN", Qt.FindChildrenRecursively)
        if self.VentasPeriodoBTN:
            self.VentasPeriodoBTN.clicked.connect(self.generar_reporte_ventas_periodo)
            self._report_buttons.append(self.VentasPeriodoBTN)

        self.TopClientesBTN = self.tabWidget.findChild(QPushButton, "TopClientesBTN", Qt.FindChildrenRecursively)
        if self.TopClientesBTN:
            self.TopClientesBTN.clicked.connect(self.generar_reporte_top_clientes)
            self._report_buttons.append(self.TopClientesBTN)

        self.MesCMB = self.tabWidget.findChild(QComboBox, "MesCMB", Qt.FindChildrenRecursively)
        if self.MesCMB:
            self.MesCMB.clear()
            self.MesCMB.addItems(
                [
                    "Enero",
                    "Febrero",
                    "Marzo",
                    "Abril",
                    "Mayo",
                    "Junio",
                    "Julio",
                    "Agosto",
                    "Septiembre",
                    "Octubre",
                    "Noviembre",
                    "Diciembre",
                ]
            )
            self.MesCMB.setCurrentIndex(QDate.currentDate().month() - 1)

        self.CategoriaCMB = self.tabWidget.findChild(QComboBox, "CategoriaCMB", Qt.FindChildrenRecursively)

        self.TipoVentaCMB = self.tabWidget.findChild(QComboBox, "TipoVentaCMB", Qt.FindChildrenRecursively)
        if self.TipoVentaCMB:
            self.TipoVentaCMB.clear()
            self.TipoVentaCMB.addItems(["Todos", "Contado", "Credito"])
            self.TipoVentaCMB.setCurrentIndex(0)
        self.FechaInicial = self.tabWidget.findChild(QDateEdit, "FechaInicial", Qt.FindChildrenRecursively)
        self.FechaFinal = self.tabWidget.findChild(QDateEdit, "FechaFinal", Qt.FindChildrenRecursively)
        if self.FechaInicial:
            self.FechaInicial.setDate(QDate.currentDate().addMonths(-1))
        if self.FechaFinal:
            self.FechaFinal.setDate(QDate.currentDate())

        self.ReporteIvaBTN = None
        scroll_area: QScrollArea | None = self.tabWidget.findChild(
            QScrollArea, "scrollArea", Qt.FindChildrenRecursively
        )
        if scroll_area and scroll_area.widget() and scroll_area.widget().layout():
            self.ReporteIvaBTN = QPushButton("Reporte IVA trimestral", scroll_area.widget())
            scroll_area.widget().layout().addWidget(self.ReporteIvaBTN)
            self.ReporteIvaBTN.clicked.connect(self.generar_reporte_iva_trimestral)
            self._report_buttons.append(self.ReporteIvaBTN)

        self._cargar_categorias_reporte()

        # Consultas
        self.ConsultaCedulaTXT = self.tabWidget.findChild(QLineEdit, "ConsultaCedulaTXT", Qt.FindChildrenRecursively)

        self.ConsultaVentasClienteBTN = self.tabWidget.findChild(QPushButton, "ConsultaVentasClienteBTN", Qt.FindChildrenRecursively)
        if self.ConsultaVentasClienteBTN:
            self.ConsultaVentasClienteBTN.clicked.connect(self.consulta_ventas_cliente)
            self._consulta_buttons.append(self.ConsultaVentasClienteBTN)

        self.ConsultaProductosBajoStockBTN = self.tabWidget.findChild(QPushButton, "ConsultaProductosBajoStockBTN", Qt.FindChildrenRecursively)
        if self.ConsultaProductosBajoStockBTN:
            self.ConsultaProductosBajoStockBTN.clicked.connect(self.consulta_productos_bajo_stock)
            self._consulta_buttons.append(self.ConsultaProductosBajoStockBTN)

        self.ConsultaCreditosActivosBTN = self.tabWidget.findChild(QPushButton, "ConsultaCreditosActivosBTN", Qt.FindChildrenRecursively)
        if self.ConsultaCreditosActivosBTN:
            self.ConsultaCreditosActivosBTN.clicked.connect(self.consulta_creditos_activos)
            self._consulta_buttons.append(self.ConsultaCreditosActivosBTN)

        self.ConsultaCuotasVencidasBTN = self.tabWidget.findChild(QPushButton, "ConsultaCuotasVencidasBTN", Qt.FindChildrenRecursively)
        if self.ConsultaCuotasVencidasBTN:
            self.ConsultaCuotasVencidasBTN.clicked.connect(self.consulta_cuotas_vencidas)
            self._consulta_buttons.append(self.ConsultaCuotasVencidasBTN)

        self.ConsultaVentasUsuarioBTN = self.tabWidget.findChild(QPushButton, "ConsultaVentasUsuarioBTN", Qt.FindChildrenRecursively)
        if self.ConsultaVentasUsuarioBTN:
            self.ConsultaVentasUsuarioBTN.clicked.connect(self.consulta_ventas_por_usuario)
            self._consulta_buttons.append(self.ConsultaVentasUsuarioBTN)

    def _cargar_categorias_reporte(self):
        if not self.CategoriaCMB:
            return
        try:
            categorias = CategoriaDAO.listar()
        except Exception as error:
            QMessageBox.warning(self, "Advertencia", f"No se pudieron cargar las categorías:\n{error}")
            return

        self.CategoriaCMB.clear()
        for categoria in categorias:
            self.CategoriaCMB.addItem(categoria.nombre, categoria.id_categoria)

    def generar_reporte_total_ventas(self):
        if not self.MesCMB:
            return
        mes_texto = self.MesCMB.currentText()
        mes_num = self._mes_texto_a_numero(mes_texto)
        if mes_num is None:
            QMessageBox.warning(self, "Dato requerido", "Seleccione un mes válido.")
            return
        try:
            columnas, filas = reporte_total_ventas_por_mes(mes_num)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{error}")
            return
        self._mostrar_tabla("Total de ventas por mes", columnas, filas)

    def generar_reporte_clientes_morosos(self):
        try:
            columnas, filas = reporte_clientes_morosos()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{error}")
            return
        self._mostrar_tabla("Clientes morosos", columnas, filas)

    def generar_reporte_inventario(self):
        if not self.CategoriaCMB:
            return
        categoria_id = self.CategoriaCMB.currentData()
        if categoria_id is None:
            QMessageBox.warning(self, "Dato requerido", "Seleccione una categoría válida.")
            return
        try:
            columnas, filas = reporte_inventario_por_categoria(categoria_id)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{error}")
            return
        self._mostrar_tabla("Inventario por categoría", columnas, filas)

    def generar_reporte_ventas_periodo(self):
        if not self.FechaInicial or not self.FechaFinal:
            return
        fecha_inicio = self.FechaInicial.date().toPython()
        fecha_fin = self.FechaFinal.date().toPython()
        if fecha_fin < fecha_inicio:
            QMessageBox.warning(self, "Fechas inválidas", "La fecha final debe ser posterior o igual a la inicial.")
            return
        tipo = self.TipoVentaCMB.currentText() if self.TipoVentaCMB else "Todos"
        if not tipo:
            tipo = "Todos"
        try:
            columnas, filas = reporte_ventas_periodo(tipo, fecha_inicio, fecha_fin)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{error}")
            return
        titulo = f"Ventas de {fecha_inicio} a {fecha_fin}"
        self._mostrar_tabla(titulo, columnas, filas)

    def generar_reporte_top_clientes(self):
        try:
            columnas, filas = reporte_top_clientes(5)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{error}")
            return
        self._mostrar_tabla("Top clientes por compras", columnas, filas)

    def consulta_ventas_cliente(self):
        if not self.ConsultaCedulaTXT:
            return
        cedula = self.ConsultaCedulaTXT.text().strip()
        if not cedula:
            QMessageBox.warning(self, "Dato requerido", "Ingrese la cédula del cliente.")
            return
        try:
            columnas, filas = consulta_ventas_por_cliente(cedula)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta:\n{error}")
            return
        self._mostrar_tabla(f"Ventas del cliente {cedula}", columnas, filas)

    def consulta_productos_bajo_stock(self):
        try:
            columnas, filas = consulta_productos_bajo_stock()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta:\n{error}")
            return
        self._mostrar_tabla("Productos con stock crítico", columnas, filas)

    def consulta_creditos_activos(self):
        try:
            columnas, filas = consulta_creditos_activos()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta:\n{error}")
            return
        self._mostrar_tabla("Créditos activos con saldo", columnas, filas)

    def consulta_cuotas_vencidas(self):
        try:
            columnas, filas = consulta_cuotas_vencidas()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta:\n{error}")
            return
        self._mostrar_tabla("Cuotas vencidas", columnas, filas)

    def consulta_ventas_por_usuario(self):
        try:
            columnas, filas = consulta_ventas_por_usuario()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta:\n{error}")
            return
        self._mostrar_tabla("Ventas por usuario", columnas, filas)

    def generar_reporte_iva_trimestral(self):
        anio_actual = QDate.currentDate().year()
        anio, ok_anio = QInputDialog.getInt(
            self,
            "Reporte IVA",
            "Ingrese el año del reporte:",
            anio_actual,
            2000,
            anio_actual + 5,
        )
        if not ok_anio:
            return

        opciones = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
        trimestre_texto, ok_trim = QInputDialog.getItem(
            self,
            "Reporte IVA",
            "Seleccione el trimestre:",
            opciones,
            (QDate.currentDate().month() - 1) // 3,
            False,
        )
        if not ok_trim or not trimestre_texto:
            return
        trimestre = opciones.index(trimestre_texto) + 1

        try:
            columnas, filas = reporte_iva_trimestral(anio, trimestre)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte de IVA:\n{error}")
            return
        titulo = f"IVA trimestre {trimestre} de {anio}"
        self._mostrar_tabla(titulo, columnas, filas)

    def _mostrar_tabla(self, titulo: str, columnas, filas):
        if not filas:
            QMessageBox.information(self, "Sin datos", "No se encontraron registros para esta operación.")
            return
        dialogo = DataTableDialog(titulo, columnas, filas, self)
        dialogo.show()
        self._result_windows.append(dialogo)

        def limpiar_referencia(_, dlg=dialogo):
            if dlg in self._result_windows:
                self._result_windows.remove(dlg)

        dialogo.destroyed.connect(limpiar_referencia)

    @staticmethod
    def _mes_texto_a_numero(texto: str | None) -> int | None:
        if not texto:
            return None
        meses = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        try:
            return meses.index(texto) + 1
        except ValueError:
            return None

    def _configurar_interfaz_segun_usuario(self):
        rol = self.usuario.rol
        self.setWindowTitle(f"{self._titulo_base} - {self.usuario.nombre}")

        if self.statusBar():
            self.statusBar().showMessage(f"Sesión: {self.usuario.nombre} | Rol: {self._obtener_nombre_rol(rol)}")

        if rol == 1:
            return

        if rol == 2:
            for boton in [self.BitacoraBTN, self.GestionUsuarioBTN]:
                if boton is not None:
                    boton.setEnabled(False)
        elif rol == 3:
            self._deshabilitar_tabs_para_esporadicos()

    def _deshabilitar_tabs_para_esporadicos(self):
        tabs_a_deshabilitar = [
            self.entidades_tab,
            self.transacciones_tab,
            self.reportes_tab,
            self.utilidades_tab,
            self.ayudas_tab,
        ]
        for tab in tabs_a_deshabilitar:
            if tab is None:
                continue
            index = self.tabWidget.indexOf(tab)
            if index != -1:
                self.tabWidget.setTabEnabled(index, False)

        if self.consultas_tab is not None:
            index_consultas = self.tabWidget.indexOf(self.consultas_tab)
            if index_consultas != -1:
                self.tabWidget.setTabEnabled(index_consultas, True)
                self.tabWidget.setCurrentWidget(self.consultas_tab)

        botones = [
            self.ClienteBTN,
            self.ProductoBTN,
            self.VentaBTN,
            self.CategoriaBTN,
            self.RegistrarVentaBTN,
            self.CreditoBTN,
            self.AgregarCuotaBTN,
            self.BitacoraBTN,
            self.GestionUsuarioBTN,
            self.CalculadoraBTN,
            self.CalendarioBTN,
        ]
        for boton in botones:
            if boton is not None:
                boton.setEnabled(False)

        for boton in self._report_buttons:
            if boton is not None:
                boton.setEnabled(False)

    @staticmethod
    def _obtener_nombre_rol(rol: int) -> str:
        return {
            1: "Administrador",
            2: "Paramétrico",
            3: "Esporádico",
        }.get(rol, "Desconocido")