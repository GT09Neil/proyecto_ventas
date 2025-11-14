from PySide6.QtWidgets import QFrame, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PySide6.QtCore import Qt


class DataTableDialog(QFrame):
    def __init__(self, titulo: str, columnas: list[str], filas: list[tuple], parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle(titulo)
        self.setMinimumSize(700, 400)

        layout = QVBoxLayout(self)

        if not columnas:
            aviso = QLabel("Sin datos disponibles", self)
            aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(aviso)
            return

        tabla = QTableWidget(self)
        tabla.setColumnCount(len(columnas))
        tabla.setRowCount(len(filas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.setAlternatingRowColors(True)

        for fila_idx, fila in enumerate(filas):
            for col_idx, valor in enumerate(fila):
                texto = "" if valor is None else str(valor)
                item = QTableWidgetItem(texto)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tabla.setItem(fila_idx, col_idx, item)

        tabla.resizeColumnsToContents()
        layout.addWidget(tabla)



