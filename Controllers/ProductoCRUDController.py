from PySide6.QtWidgets import (
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QPushButton,
    QComboBox,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt

from dao.producto_dao import ProductoDAO
from dao.categoria_dao import CategoriaDAO
from modelos.producto import Producto


class ProductoCRUDController(QFrame):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("GUI/ProductoCRUD.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.resize(self.ui.size())
        self.setFixedSize(self.size())

        screen = QGuiApplication.primaryScreen().geometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        self.tabla: QTableWidget = self.ui.findChild(QTableWidget, "TablaProductos")
        self.codigo_txt: QLineEdit = self.ui.findChild(QLineEdit, "CodigoTXT")
        self.nombre_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreTXT")
        self.valor_venta_txt: QLineEdit = self.ui.findChild(QLineEdit, "ValorVentaTXT")
        self.valor_adq_txt: QLineEdit = self.ui.findChild(QLineEdit, "ValorAdquisicionTXT")

        # Adaptar campo de categoría: usar combo si existe, de lo contrario usar QLineEdit
        self.categoria_cmb: QComboBox | None = self.ui.findChild(QComboBox, "CategoriaCMB")
        self.categoria_txt: QLineEdit | None = self.ui.findChild(QLineEdit, "CategoriaTXT")

        self.agregar_btn: QPushButton = self.ui.findChild(QPushButton, "AgregarBTN")
        self.actualizar_btn: QPushButton = self.ui.findChild(QPushButton, "ActualizarBTN")
        self.eliminar_btn: QPushButton = self.ui.findChild(QPushButton, "EliminarBTN")

        self._producto_en_edicion: Producto | None = None
        self._categorias = []

        self._cargar_categorias()
        self._configurar_tabla()
        self._conectar_eventos()
        self.cargar_productos()

        self.show()

    def _cargar_categorias(self):
        try:
            self._categorias = CategoriaDAO.listar()
        except Exception as error:
            QMessageBox.warning(self, "Advertencia", f"No se pudieron cargar categorías:\n{error}")
            self._categorias = []

        if self.categoria_cmb:
            self.categoria_cmb.clear()
            for categoria in self._categorias:
                self.categoria_cmb.addItem(categoria.nombre, categoria.id_categoria)

    def _configurar_tabla(self):
        if not self.tabla:
            return
        self.tabla.setSortingEnabled(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.itemSelectionChanged.connect(self._al_seleccionar_fila)

    def _conectar_eventos(self):
        if self.agregar_btn:
            self.agregar_btn.clicked.connect(self._agregar_producto)
        if self.actualizar_btn:
            self.actualizar_btn.clicked.connect(self._actualizar_producto)
        if self.eliminar_btn:
            self.eliminar_btn.clicked.connect(self._eliminar_producto)

    def cargar_productos(self):
        if not self.tabla:
            return
        try:
            productos = ProductoDAO.listar()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos:\n{error}")
            return

        cat_por_id = {c.id_categoria: c.nombre for c in self._categorias}
        self.tabla.setRowCount(len(productos))
        for fila, producto in enumerate(productos):
            datos = [
                producto.codigo,
                producto.nombre,
                cat_por_id.get(producto.id_categoria, str(producto.id_categoria)),
                f"{producto.valor_adquisicion:.2f}",
                f"{producto.valor_venta:.2f}",
            ]
            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor if valor is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def _obtener_categoria_seleccionada(self) -> int | None:
        if self.categoria_cmb:
            return self.categoria_cmb.currentData()
        if self.categoria_txt:
            texto = self.categoria_txt.text().strip()
            return int(texto) if texto.isdigit() else None
        return None

    def _obtener_datos_formulario(self) -> Producto | None:
        codigo = self.codigo_txt.text().strip() if self.codigo_txt else ""
        nombre = self.nombre_txt.text().strip() if self.nombre_txt else ""
        categoria_id = self._obtener_categoria_seleccionada()
        valor_adq = self.valor_adq_txt.text().strip() if self.valor_adq_txt else "0"
        valor_venta = self.valor_venta_txt.text().strip() if self.valor_venta_txt else "0"

        if not codigo or not nombre or categoria_id is None:
            QMessageBox.warning(self, "Campos requeridos", "Código, nombre y categoría son obligatorios.")
            return None

        try:
            valor_adq_float = float(valor_adq)
            valor_venta_float = float(valor_venta)
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "Ingrese valores numéricos para los precios.")
            return None

        producto = Producto(
            id_producto=self._producto_en_edicion.id_producto if self._producto_en_edicion else None,
            codigo=codigo,
            nombre=nombre,
            id_categoria=categoria_id,
            valor_adquisicion=valor_adq_float,
            valor_venta=valor_venta_float,
            stock=self._producto_en_edicion.stock if self._producto_en_edicion else 0,
        )
        return producto

    def _agregar_producto(self):
        producto = self._obtener_datos_formulario()
        if producto is None:
            return

        try:
            existente = ProductoDAO.buscar_por_codigo(producto.codigo)
            if existente:
                QMessageBox.warning(self, "Duplicado", "Ya existe un producto con ese código.")
                return
            ProductoDAO.agregar(producto)
            self.cargar_productos()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto:\n{error}")

    def _actualizar_producto(self):
        if not self._producto_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione un producto.")
            return

        producto = self._obtener_datos_formulario()
        if producto is None:
            return

        producto.id_producto = self._producto_en_edicion.id_producto
        producto.stock = self._producto_en_edicion.stock

        try:
            ProductoDAO.actualizar(producto)
            self.cargar_productos()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto:\n{error}")

    def _eliminar_producto(self):
        if not self._producto_en_edicion:
            QMessageBox.warning(self, "Selección requerida", "Seleccione un producto para eliminarlo.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar el producto {self._producto_en_edicion.nombre}?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            ProductoDAO.eliminar(self._producto_en_edicion.id_producto)
            self.cargar_productos()
            self._limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto eliminado.")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto:\n{error}")

    def _al_seleccionar_fila(self):
        if not self.tabla or not self.tabla.selectionModel():
            return
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return

        fila = filas[0].row()
        codigo = self.tabla.item(fila, 0).text()
        producto = ProductoDAO.buscar_por_codigo(codigo)
        if not producto:
            return

        self._producto_en_edicion = producto
        if self.codigo_txt:
            self.codigo_txt.setText(producto.codigo)
        if self.nombre_txt:
            self.nombre_txt.setText(producto.nombre)
        if self.valor_adq_txt:
            self.valor_adq_txt.setText(f"{producto.valor_adquisicion:.2f}")
        if self.valor_venta_txt:
            self.valor_venta_txt.setText(f"{producto.valor_venta:.2f}")

        if self.categoria_cmb:
            index = self.categoria_cmb.findData(producto.id_categoria)
            if index != -1:
                self.categoria_cmb.setCurrentIndex(index)
        elif self.categoria_txt:
            self.categoria_txt.setText(str(producto.id_categoria))

    def _limpiar_formulario(self):
        self._producto_en_edicion = None
        for widget in [self.codigo_txt, self.nombre_txt, self.valor_adq_txt, self.valor_venta_txt]:
            if widget:
                widget.clear()
        if self.categoria_cmb and self.categoria_cmb.count():
            self.categoria_cmb.setCurrentIndex(0)
        if self.categoria_txt:
            self.categoria_txt.clear()
        if self.tabla:
            self.tabla.clearSelection()