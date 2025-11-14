from PySide6.QtWidgets import QFrame, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, QRect
from Controllers.VentanaPrincipalController import VentanaPrincipalController

from dao.usuario_dao import UsuarioDAO
from dao.bitacora_dao import BitacoraDAO


class LoginController(QFrame):
    def __init__(self):
        super().__init__()

        # Cargar la interfaz desde el archivo .ui
        loader = QUiLoader()
        file = QFile("GUI/Login.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())


        # Conectar el botón de inicio de sesión a la función correspondiente
        self.ui.AccederBTN.clicked.connect(self.iniciar_sesion)

        # Mostrar la ventana
        self.show()

    def iniciar_sesion(self):
        cedula = self.ui.CedulaTXT.text().strip()
        contrasena = self.ui.ContrasenaTXT.text()

        if not cedula or not contrasena:
            QMessageBox.warning(self, "Credenciales inválidas", "Ingrese cédula y contraseña.")
            return

        try:
            usuario = UsuarioDAO.autenticar(cedula, contrasena)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos:\n{error}")
            return

        if not usuario:
            QMessageBox.critical(self, "Acceso denegado", "Cédula o contraseña incorrectas, o usuario inactivo.")
            return

        try:
            UsuarioDAO.actualizar_ultimo_acceso(usuario.id_usuario)
            BitacoraDAO.registrar(usuario.id_usuario, "Login", "Ingreso al sistema")
        except Exception as error:
            QMessageBox.warning(self, "Advertencia", f"No se pudo actualizar la bitácora:\n{error}")

        # Si la autenticación es exitosa, abrir la ventana principal
        self.ventana_principal = VentanaPrincipalController(usuario)
        self.ventana_principal.show()

        # Cerrar la ventana de inicio de sesión
        self.close()