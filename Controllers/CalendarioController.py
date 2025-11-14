from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QCalendarWidget
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QDate, Qt


class CalendarioController(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendario")
        self.setMinimumSize(400, 350)

        layout = QVBoxLayout(self)

        self.calendario = QCalendarWidget(self)
        self.calendario.setGridVisible(True)
        self.calendario.selectionChanged.connect(self._actualizar_label)
        layout.addWidget(self.calendario)

        self.label_fecha = QLabel(self)
        self.label_fecha.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_fecha)

        self._actualizar_label()

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.show()

    def _actualizar_label(self):
        fecha = self.calendario.selectedDate()
        self.label_fecha.setText(f"Fecha seleccionada: {fecha.toString('dddd, dd MMMM yyyy')}")

