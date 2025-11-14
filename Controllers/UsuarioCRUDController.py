from PySide6.QtWidgets import (
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QLineEdit,
    QPushButton,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.usuario_dao import UsuarioDAO
from modelos.usuario import Usuario


class UsuarioCRUDController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/UsuarioCRUD.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.tabla: QTableWidget = self.ui.findChild(QTableWidget, "TablaUsuarios")
        self.cedula_txt: QLineEdit = self.ui.findChild(QLineEdit, "CedulaTXT")
        if self.cedula_txt is None:
            self.cedula_txt = self.ui.findChild(QLineEdit, "idTXT")
            if self.cedula_txt:
                self.cedula_txt.setPlaceholderText("Cédula")
        self.nombre_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreTXT")
        self.email_txt: QLineEdit = self.ui.findChild(QLineEdit, "EmailTXT")
        self.password_txt: QLineEdit = self.ui.findChild(QLineEdit, "ContrasenaTXT")
        self.rol_cmb: QComboBox = self.ui.findChild(QComboBox, "TipoUsuarioCMB")
        self.estado_cmb: QComboBox = self.ui.findChild(QComboBox, "EstadoCMB")

        self.agregar_btn: QPushButton = self.ui.findChild(QPushButton, "AgregarBTN")
        self.actualizar_btn: QPushButton = self.ui.findChild(QPushButton, "ActualizarBTN")

        self._usuario_en_edicion_id: int | None = None

        self._configurar_comboboxes()
        self._configurar_tabla()
        self._conectar_eventos()
        self.cargar_usuarios()

        self.show()

    def _configurar_comboboxes(self):
        self.rol_cmb.clear()
        self.rol_cmb.addItem("Administrador", 1)
        self.rol_cmb.addItem("Paramétrico", 2)
        self.rol_cmb.addItem("Esporádico", 3)

    def _configurar_tabla(self):
        if not self.tabla:
            return
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Cédula", "Nombre", "Email", "Rol", "Estado"]
        )
        self.tabla.setSortingEnabled(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.itemSelectionChanged.connect(self._al_seleccionar_fila)

    def _conectar_eventos(self):
        if self.agregar_btn:
            self.agregar_btn.clicked.connect(self._agregar_usuario)
        if self.actualizar_btn:
            self.actualizar_btn.clicked.connect(self._actualizar_usuario)

    def cargar_usuarios(self):
        if not self.tabla:
            return
        try:
            usuarios = UsuarioDAO.listar()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los usuarios:\n{error}")
            return

        self.tabla.setRowCount(len(usuarios))
        for fila, usuario in enumerate(usuarios):
            datos = [
                str(usuario.id_usuario),
                usuario.cedula,
                usuario.nombre,
                usuario.email,
                self._nombre_rol(usuario.rol),
                usuario.estado,
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla.setItem(fila, columna, item)

        self.tabla.resizeColumnsToContents()

    def _recopilar_datos_formulario(self) -> Usuario | None:
        cedula = self.cedula_txt.text().strip() if self.cedula_txt else ""
        nombre = self.nombre_txt.text().strip()
        email = self.email_txt.text().strip()
        estado = self.estado_cmb.currentText()
        rol = self.rol_cmb.currentData()

        if not cedula or not nombre or not email:
            QMessageBox.warning(self, "Campos incompletos", "Cédula, nombre y email son obligatorios.")
            return None

        usuario = Usuario(
            id_usuario=self._usuario_en_edicion_id,
            cedula=cedula,
            nombre=nombre,
            email=email,
            rol=rol,
            estado=estado,
        )
        return usuario

    def _agregar_usuario(self):
        usuario = self._recopilar_datos_formulario()
        if usuario is None:
            return

        password = self.password_txt.text()
        if not password:
            QMessageBox.warning(self, "Contraseña requerida", "Ingrese una contraseña para el nuevo usuario.")
            return

        try:
            nuevo_id = UsuarioDAO.crear(usuario, password)
            usuario.id_usuario = nuevo_id
            self.cargar_usuarios()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Usuario creado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo crear el usuario:\n{error}")

    def _actualizar_usuario(self):
        usuario = self._recopilar_datos_formulario()
        if usuario is None:
            return

        if usuario.id_usuario is None:
            QMessageBox.warning(self, "Seleccionar usuario", "Seleccione un usuario de la tabla para actualizarlo.")
            return

        password = self.password_txt.text().strip()
        password = password if password else None

        try:
            UsuarioDAO.actualizar(usuario, password)
            self.cargar_usuarios()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el usuario:\n{error}")

    def _al_seleccionar_fila(self):
        if not self.tabla or not self.tabla.selectionModel():
            return
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return

        fila = filas[0].row()
        self._usuario_en_edicion_id = int(self.tabla.item(fila, 0).text())
        if self.cedula_txt:
            self.cedula_txt.setText(self.tabla.item(fila, 1).text())
        self.nombre_txt.setText(self.tabla.item(fila, 2).text())
        self.email_txt.setText(self.tabla.item(fila, 3).text())

        rol_texto = self.tabla.item(fila, 4).text()
        index_rol = self.rol_cmb.findText(rol_texto)
        if index_rol != -1:
            self.rol_cmb.setCurrentIndex(index_rol)

        estado_texto = self.tabla.item(fila, 5).text()
        index_estado = self.estado_cmb.findText(estado_texto)
        if index_estado != -1:
            self.estado_cmb.setCurrentIndex(index_estado)

        self.password_txt.clear()

    def _limpiar_formulario(self):
        self._usuario_en_edicion_id = None
        if self.cedula_txt:
            self.cedula_txt.clear()
        self.nombre_txt.clear()
        self.email_txt.clear()
        self.password_txt.clear()
        self.rol_cmb.setCurrentIndex(0)
        self.estado_cmb.setCurrentIndex(0)
        if self.tabla:
            self.tabla.clearSelection()

    @staticmethod
    def _nombre_rol(rol: int) -> str:
        return {
            1: "Administrador",
            2: "Paramétrico",
            3: "Esporádico",
        }.get(rol, "Desconocido")