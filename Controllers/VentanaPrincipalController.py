from PySide6.QtWidgets import QMainWindow, QPushButton, QTabWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt, QRect

from Controllers.ClienteCRUDController import ClienteCRUDController
from Controllers.ProductoCRUDController import ProductoCRUDController
from Controllers.VentasCRUDController import VentasCRUDController
from Controllers.CategoriaCRUDController import CategoriaCRUDController
from Controllers.RegistrarVentaController import RegistrarVentaController
from Controllers.CreditosController import CreditosController
from Controllers.CuotasController import CuotasController
from Controllers.BitacoraController import BitacoraController
from Controllers.UsuarioCRUDController import UsuarioCRUDController


class VentanaPrincipalController(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cargar la interfaz desde el archivo .ui
        loader = QUiLoader()
        file = QFile("GUI/VentanaPrincipal.ui")
        file.open(QFile.ReadOnly)
        loaded_ui = loader.load(file)
        file.close()

        self.setCentralWidget(loaded_ui.centralWidget())
        self.tabWidget = self.centralWidget().findChild(QTabWidget, "tabWidget")
        self.setWindowTitle(loaded_ui.windowTitle())
        self.resize(loaded_ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.ClienteBTN = self.tabWidget.findChild(QPushButton, "ClienteBTN", Qt.FindChildrenRecursively)
        self.ClienteBTN.clicked.connect(self.abrir_CRUD_clientes)

        self.ProductoBTN = self.tabWidget.findChild(QPushButton, "ProductoBTN", Qt.FindChildrenRecursively)
        self.ProductoBTN.clicked.connect(self.abrir_CRUD_productos)

        self.VentaBTN = self.tabWidget.findChild(QPushButton, "VentaBTN")
        self.VentaBTN.clicked.connect(self.abrir_CRUD_ventas)

        self.CategoriaBTN = self.tabWidget.findChild(QPushButton, "CategoriaBTN", Qt.FindChildrenRecursively)
        self.CategoriaBTN.clicked.connect(self.abrir_CRUD_categorias)

        self.RegistrarVentaBTN = self.tabWidget.findChild(QPushButton, "RegistrarVentaBTN", Qt.FindChildrenRecursively)
        self.RegistrarVentaBTN.clicked.connect(self.abrir_registrar_venta)

        self.CreditoBTN = self.tabWidget.findChild(QPushButton, "CreditoBTN", Qt.FindChildrenRecursively)
        self.CreditoBTN.clicked.connect(self.abrir_creditos)

        self.AgregarCuotaBTN = self.tabWidget.findChild(QPushButton, "AgregarCuotaBTN", Qt.FindChildrenRecursively)
        self.AgregarCuotaBTN.clicked.connect(self.abrir_cuotas)

        self.BitacoraBTN = self.tabWidget.findChild(QPushButton, "BitacoraBTN", Qt.FindChildrenRecursively)
        self.BitacoraBTN.clicked.connect(self.abrir_bitacora)

        self.GestionUsuarioBTN = self.tabWidget.findChild(QPushButton, "GestionUsuarioBTN", Qt.FindChildrenRecursively)
        self.GestionUsuarioBTN.clicked.connect(self.abrir_CRUD_usuarios)

        self.CalculadoraBTN = self.tabWidget.findChild(QPushButton, "CalculadoraBTN", Qt.FindChildrenRecursively)
        self.CalculadoraBTN.clicked.connect(self.abrir_calculadora)

        # Conectar señales y slots aquí si es necesario
        # Ejemplo: self.botonEjemplo.clicked.connect(self.funcionEjemplo)

        # Mostrar la ventana
        self.show()

    def abrir_CRUD_clientes(self):
        
        self.cliente_crud = ClienteCRUDController()
        self.cliente_crud.show()

    def abrir_CRUD_productos(self):
        self.producto_crud = ProductoCRUDController()
        self.producto_crud.show()

    def abrir_CRUD_ventas(self):
        self.venta_crud = VentasCRUDController()
        self.venta_crud.show()

    def abrir_CRUD_categorias(self):
        self.categoria_crud = CategoriaCRUDController()
        self.categoria_crud.show()
    
    def abrir_registrar_venta(self):
        self.registrar_venta = RegistrarVentaController()
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