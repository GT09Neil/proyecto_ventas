from PySide6.QtWidgets import (
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QPushButton,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.categoria_dao import CategoriaDAO
from modelos.categoria import Categoria


class CategoriaCRUDController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/CategoriaCRUD.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.tabla: QTableWidget = self.ui.findChild(QTableWidget, "tablaCategorias")
        self.id_txt: QLineEdit = self.ui.findChild(QLineEdit, "idCategoriaTXT")
        self.nombre_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreCategoriaTXT")
        self.iva_txt: QLineEdit = self.ui.findChild(QLineEdit, "ivaTXT")
        self.utilidad_txt: QLineEdit = self.ui.findChild(QLineEdit, "UtilidadTXT")

        self.agregar_btn: QPushButton = self.ui.findChild(QPushButton, "AgregarBTN")
        self.actualizar_btn: QPushButton = self.ui.findChild(QPushButton, "ActualizarBTN")
        self.eliminar_btn: QPushButton = self.ui.findChild(QPushButton, "EliminarBTN")

        self._categoria_en_edicion: Categoria | None = None

        self._configurar_tabla()
        self._conectar_eventos()
        self.cargar_categorias()

        self.show()

    def _configurar_tabla(self):
        if not self.tabla:
            return
        self.tabla.setSortingEnabled(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.itemSelectionChanged.connect(self._al_seleccionar_fila)

    def _conectar_eventos(self):
        if self.agregar_btn:
            self.agregar_btn.clicked.connect(self._agregar_categoria)
        if self.actualizar_btn:
            self.actualizar_btn.clicked.connect(self._actualizar_categoria)
        if self.eliminar_btn:
            self.eliminar_btn.clicked.connect(self._eliminar_categoria)

    def cargar_categorias(self):
        if not self.tabla:
            return
        try:
            categorias = CategoriaDAO.listar()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las categorías:\n{error}")
            return

        self.tabla.setRowCount(len(categorias))
        for fila, categoria in enumerate(categorias):
            datos = [
                str(categoria.id_categoria),
                categoria.nombre,
                f"{categoria.iva:.2f}",
                f"{categoria.utilidad:.2f}",
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor if valor is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def _obtener_datos_formulario(self) -> Categoria | None:
        nombre = self.nombre_txt.text().strip() if self.nombre_txt else ""
        iva_texto = self.iva_txt.text().strip() if self.iva_txt else "0"
        utilidad_texto = self.utilidad_txt.text().strip() if self.utilidad_txt else "0"

        if not nombre:
            QMessageBox.warning(self, "Campos requeridos", "El nombre es obligatorio.")
            return None

        try:
            iva = float(iva_texto)
            utilidad = float(utilidad_texto)
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "IVA y utilidad deben ser numéricos.")
            return None

        categoria = Categoria(
            id_categoria=self._categoria_en_edicion.id_categoria if self._categoria_en_edicion else None,
            nombre=nombre,
            iva=iva,
            utilidad=utilidad,
        )
        return categoria

    def _agregar_categoria(self):
        categoria = self._obtener_datos_formulario()
        if categoria is None:
            return

        try:
            nuevo_id = CategoriaDAO.crear(categoria)
            categoria.id_categoria = nuevo_id
            self.cargar_categorias()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Categoría creada correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo crear la categoría:\n{error}")

    def _actualizar_categoria(self):
        if not self._categoria_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione una categoría para actualizar.")
            return

        categoria = self._obtener_datos_formulario()
        if categoria is None:
            return

        categoria.id_categoria = self._categoria_en_edicion.id_categoria

        try:
            CategoriaDAO.actualizar(categoria)
            self.cargar_categorias()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Categoría actualizada correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la categoría:\n{error}")

    def _eliminar_categoria(self):
        if not self._categoria_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione una categoría para eliminarla.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar la categoría {self._categoria_en_edicion.nombre}?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            CategoriaDAO.eliminar(self._categoria_en_edicion.id_categoria)
            self.cargar_categorias()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Categoría eliminada.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la categoría:\n{error}")

    def _al_seleccionar_fila(self):
        if not self.tabla or not self.tabla.selectionModel():
            return
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return

        fila = filas[0].row()
        id_categoria = int(self.tabla.item(fila, 0).text())
        categoria = CategoriaDAO.obtener_por_id(id_categoria)
        if not categoria:
            return

        self._categoria_en_edicion = categoria
        if self.id_txt:
            self.id_txt.setText(str(categoria.id_categoria))
        if self.nombre_txt:
            self.nombre_txt.setText(categoria.nombre)
        if self.iva_txt:
            self.iva_txt.setText(f"{categoria.iva:.2f}")
        if self.utilidad_txt:
            self.utilidad_txt.setText(f"{categoria.utilidad:.2f}")

    def _limpiar_formulario(self):
        self._categoria_en_edicion = None
        for widget in [self.id_txt, self.nombre_txt, self.iva_txt, self.utilidad_txt]:
            if widget:
                widget.clear()
        if self.tabla:
            self.tabla.clearSelection()