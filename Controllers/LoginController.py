from PySide6.QtWidgets import QFrame
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, QRect
from Controllers.VentanaPrincipalController import VentanaPrincipalController

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
        # Aquí iría la lógica de autenticación (verificación de usuario y contraseña)
        # Por simplicidad, asumimos que la autenticación es exitosa

        # Si la autenticación es exitosa, abrir la ventana principal
        self.ventana_principal = VentanaPrincipalController()
        self.ventana_principal.show()

        # Cerrar la ventana de inicio de sesión
        self.close()