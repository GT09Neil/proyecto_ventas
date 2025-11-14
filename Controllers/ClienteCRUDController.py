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

from dao.cliente_dao import ClienteDAO
from modelos.cliente import Cliente


class ClienteCRUDController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/ClienteCRUD.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.tabla: QTableWidget = self.ui.findChild(QTableWidget, "tablaClientes")
        self.cedula_txt: QLineEdit = self.ui.findChild(QLineEdit, "CedulaTXT")
        self.nombre_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreTXT")
        self.direccion_txt: QLineEdit = self.ui.findChild(QLineEdit, "DireccionTXT")
        self.email_txt: QLineEdit = self.ui.findChild(QLineEdit, "EmailTXT")

        self.agregar_btn: QPushButton = self.ui.findChild(QPushButton, "AgregarBTN")
        self.actualizar_btn: QPushButton = self.ui.findChild(QPushButton, "ActualizarBTN")
        self.eliminar_btn: QPushButton = self.ui.findChild(QPushButton, "EliminarBTN")

        self._cliente_en_edicion: Cliente | None = None

        self._configurar_tabla()
        self._conectar_eventos()
        self.cargar_clientes()

        self.show()

    def _configurar_tabla(self):
        if not self.tabla:
            return
        self.tabla.setSortingEnabled(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.itemSelectionChanged.connect(self._al_seleccionar_fila)

    def _conectar_eventos(self):
        if self.agregar_btn:
            self.agregar_btn.clicked.connect(self._agregar_cliente)
        if self.actualizar_btn:
            self.actualizar_btn.clicked.connect(self._actualizar_cliente)
        if self.eliminar_btn:
            self.eliminar_btn.clicked.connect(self._eliminar_cliente)

    def cargar_clientes(self):
        if not self.tabla:
            return
        try:
            clientes = ClienteDAO.listar()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los clientes:\n{error}")
            return

        self.tabla.setRowCount(len(clientes))
        for fila, cliente in enumerate(clientes):
            datos = [
                cliente.cedula,
                cliente.nombre,
                cliente.direccion,
                cliente.email,
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor if valor is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def _obtener_datos_formulario(self) -> Cliente | None:
        cedula = self.cedula_txt.text().strip() if self.cedula_txt else ""
        nombre = self.nombre_txt.text().strip()
        direccion = self.direccion_txt.text().strip() if self.direccion_txt else ""
        email = self.email_txt.text().strip()
        telefono = self._cliente_en_edicion.telefono if self._cliente_en_edicion else ""

        if not cedula or not nombre:
            QMessageBox.warning(self, "Campos requeridos", "Cédula y nombre son obligatorios.")
            return None

        cliente = Cliente(
            id_cliente=self._cliente_en_edicion.id_cliente if self._cliente_en_edicion else None,
            nombre=nombre,
            cedula=cedula,
            direccion=direccion,
            telefono=telefono,
            email=email,
        )
        return cliente

    def _agregar_cliente(self):
        cliente = self._obtener_datos_formulario()
        if cliente is None:
            return

        try:
            existente = ClienteDAO.buscar_por_cedula(cliente.cedula)
            if existente:
                QMessageBox.warning(self, "Duplicado", "Ya existe un cliente con esa cédula.")
                return
            ClienteDAO.agregar(cliente)
            self.cargar_clientes()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el cliente:\n{error}")

    def _actualizar_cliente(self):
        if not self._cliente_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione un cliente de la tabla.")
            return

        cliente = self._obtener_datos_formulario()
        if cliente is None:
            return

        cliente.id_cliente = self._cliente_en_edicion.id_cliente

        try:
            ClienteDAO.actualizar(cliente)
            self.cargar_clientes()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el cliente:\n{error}")

    def _eliminar_cliente(self):
        if not self._cliente_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione un cliente para eliminarlo.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar al cliente {self._cliente_en_edicion.nombre}?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            ClienteDAO.eliminar(self._cliente_en_edicion.id_cliente)
            self.cargar_clientes()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Cliente eliminado.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el cliente:\n{error}")

    def _al_seleccionar_fila(self):
        if not self.tabla or not self.tabla.selectionModel():
            return
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return

        fila = filas[0].row()
        cedula = self.tabla.item(fila, 0).text()
        cliente = ClienteDAO.buscar_por_cedula(cedula)
        if not cliente:
            return

        self._cliente_en_edicion = cliente
        if self.cedula_txt:
            self.cedula_txt.setText(cliente.cedula)
        if self.nombre_txt:
            self.nombre_txt.setText(cliente.nombre)
        if self.direccion_txt:
            self.direccion_txt.setText(cliente.direccion or "")
        if self.email_txt:
            self.email_txt.setText(cliente.email or "")

    def _limpiar_formulario(self):
        self._cliente_en_edicion = None
        if self.cedula_txt:
            self.cedula_txt.clear()
        if self.nombre_txt:
            self.nombre_txt.clear()
        if self.direccion_txt:
            self.direccion_txt.clear()
        if self.email_txt:
            self.email_txt.clear()
        if self.tabla:
            self.tabla.clearSelection()