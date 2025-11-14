from PySide6.QtWidgets import QFrame, QTableWidget, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.bitacora_dao import BitacoraDAO


class BitacoraController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/Bitacora.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.tabla: QTableWidget = self.ui.findChild(QTableWidget, "TablaBitacora")
        self._configurar_tabla()
        self.cargar_registros()

        self.show()

    def _configurar_tabla(self):
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID Registro", "Fecha/Hora", "Evento", "Detalle", "ID Usuario", "Usuario"]
        )
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSortingEnabled(True)

    def cargar_registros(self):
        registros = BitacoraDAO.listar()
        self.tabla.setRowCount(len(registros))

        for fila, registro in enumerate(registros):
            rol = self._obtener_nombre_rol(registro.rol)
            usuario_detalle = f"{registro.nombre} ({rol})"

            valores = [
                str(registro.id_bitacora),
                registro.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if registro.fecha_hora else "",
                str(registro.tipo_evento),
                str(registro.detalle),
                str(registro.id_usuario),
                usuario_detalle,
            ]

            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla.setItem(fila, columna, item)

        self.tabla.resizeColumnsToContents()

    @staticmethod
    def _obtener_nombre_rol(rol: int) -> str:
        return {
            1: "Administrador",
            2: "Paramétrico",
            3: "Esporádico",
        }.get(rol, "Desconocido")