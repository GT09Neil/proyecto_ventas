from modelos.cliente import Cliente
from dao.cliente_dao import ClienteDAO
from PySide6.QtWidgets import QApplication
from Controllers.LoginController import LoginController
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginController()
    sys.exit(app.exec())


# Agregar cliente
# nuevo = Cliente(nombre="Carlos Pérez", cedula="123456789", direccion="Calle 10 #20", telefono="3214567890", email="carlos@mail.com")
# ClienteDAO.agregar(nuevo)

# Listar clientes
# print("📋 Lista de clientes:")
# for c in ClienteDAO.listar():
#    print(c)

# Actualizar cliente
# primero = ClienteDAO.listar()[0]
# primero.nombre = "Carlos Pérez Editado"
# ClienteDAO.actualizar(primero)

# Eliminar cliente
# ClienteDAO.eliminar(0)  # 👈 Descomenta para probar borrado


