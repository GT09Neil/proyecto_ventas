from PySide6.QtWidgets import QApplication
from Controllers.LoginController import LoginController
import sys
from data_initializer import DataInitializer

if __name__ == "__main__":
    initializer = DataInitializer()
    initializer.run()
    if initializer.errores:
        print("Advertencias durante la carga de datos iniciales:")
        for mensaje in initializer.errores:
            print(f" - {mensaje}")

    app = QApplication(sys.argv)
    login = LoginController()
    sys.exit(app.exec())

