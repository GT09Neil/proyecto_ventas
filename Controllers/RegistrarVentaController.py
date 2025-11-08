from PySide6.QtWidgets import QFrame
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, QRect

class RegistrarVentaController(QFrame):
    def __init__(self):
        super().__init__()

        # Cargar la interfaz desde el archivo .ui
        loader = QUiLoader()
        file = QFile("GUI/RegistrarVenta.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        # Mostrar el frame
        self.show()