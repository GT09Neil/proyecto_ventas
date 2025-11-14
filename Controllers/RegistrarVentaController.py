from datetime import datetime

from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QFile, Qt, QDate

from dao.cliente_dao import ClienteDAO
from dao.producto_dao import ProductoDAO
from dao.categoria_dao import CategoriaDAO
from dao.venta_dao import VentaDAO
from dao.detalle_venta_dao import DetalleVentaDAO
from dao.credito_dao import CreditoDAO
from dao.cuota_dao import CuotaDAO
from modelos.venta import Venta
from modelos.detalle_venta import DetalleVenta
from modelos.credito import Credito
from modelos.cuota import Cuota
from Controllers.FacturaDialog import FacturaDialog
from reportes.factura import generar_datos_factura


class RegistrarVentaController(QFrame):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.cliente_actual = None
        self.detalles = []
        self.productos = []
        self.productos_por_id = {}
        self._facturas_emitidas: list[FacturaDialog] = []

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

        # Widgets
        self.cedula_txt: QLineEdit = self.ui.findChild(QLineEdit, "cedulaTXT")
        self.buscar_btn: QPushButton = self.ui.findChild(QPushButton, "BuscarBTN")
        self.fecha_edit: QDateEdit = self.ui.findChild(QDateEdit, "fechaVenta")
        self.contado_btn: QRadioButton = self.ui.findChild(QRadioButton, "ContadoBTN")
        self.credito_btn: QRadioButton = self.ui.findChild(QRadioButton, "CreditoBTN")
        self.nombre_cliente_txt: QLineEdit = self.ui.findChild(QLineEdit, "NombreCTXT")
        self.direccion_cliente_txt: QLineEdit = self.ui.findChild(QLineEdit, "DireccionCTXT")
        self.email_cliente_txt: QLineEdit = self.ui.findChild(QLineEdit, "EmailCTXT")
        self.telefono_cliente_txt: QLineEdit = self.ui.findChild(QLineEdit, "TelefonoCTXT")
        self.total_txt: QLineEdit = self.ui.findChild(QLineEdit, "totalVentatxt")
        self.agregar_detalle_btn: QPushButton = self.ui.findChild(QPushButton, "AgregarDetalleVBTN")
        self.eliminar_detalle_btn: QPushButton = self.ui.findChild(QPushButton, "EliminarDetalleVBTN")
        self.registrar_btn: QPushButton = self.ui.findChild(QPushButton, "RegitrarBTN")
        self.tabla_detalle: QTableWidget = self.ui.findChild(QTableWidget, "TablaDetalleVenta")
        self.tabla_productos: QTableWidget = self.ui.findChild(QTableWidget, "TablaProductos")

        if self.fecha_edit:
            self.fecha_edit.setDate(QDate.currentDate())
        if self.contado_btn:
            self.contado_btn.setChecked(True)

        self._configurar_tablas()
        self._conectar_eventos()
        self._cargar_productos()
        self._refrescar_detalle()

        self.show()

    def _configurar_tablas(self):
        if self.tabla_productos:
            self.tabla_productos.setColumnCount(5)
            self.tabla_productos.setHorizontalHeaderLabels(
                ["ID", "Código", "Producto", "Categoría", "Stock"]
            )
            self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.tabla_productos.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        if self.tabla_detalle:
            self.tabla_detalle.setColumnCount(5)
            self.tabla_detalle.setHorizontalHeaderLabels(
                ["ID", "Producto", "Cantidad", "Precio", "Subtotal"]
            )
            self.tabla_detalle.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.tabla_detalle.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self.tabla_detalle.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def _conectar_eventos(self):
        if self.buscar_btn:
            self.buscar_btn.clicked.connect(self._buscar_cliente)
        if self.agregar_detalle_btn:
            self.agregar_detalle_btn.clicked.connect(self._agregar_detalle)
        if self.eliminar_detalle_btn:
            self.eliminar_detalle_btn.clicked.connect(self._eliminar_detalle)
        if self.registrar_btn:
            self.registrar_btn.clicked.connect(self._registrar_venta)

    def _cargar_productos(self):
        try:
            self.productos = ProductoDAO.listar()
            categorias = {c.id_categoria: c.nombre for c in CategoriaDAO.listar()}
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos:\n{error}")
            self.productos = []
            categorias = {}

        self.productos_por_id = {p.id_producto: p for p in self.productos}

        if not self.tabla_productos:
            return

        self.tabla_productos.setRowCount(len(self.productos))
        for fila, producto in enumerate(self.productos):
            datos = [
                producto.id_producto,
                producto.codigo,
                producto.nombre,
                categorias.get(producto.id_categoria, ""),
                producto.stock,
            ]
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabla_productos.setItem(fila, col, item)
        self.tabla_productos.resizeColumnsToContents()

    def _buscar_cliente(self):
        if not self.cedula_txt:
            return
        cedula = self.cedula_txt.text().strip()
        if not cedula:
            QMessageBox.warning(self, "Dato requerido", "Ingrese la cédula del cliente.")
            return
        try:
            cliente = ClienteDAO.buscar_por_cedula(cedula)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo consultar el cliente:\n{error}")
            return
        if not cliente:
            QMessageBox.information(self, "Sin resultados", "No se encontró un cliente con esa cédula.")
            return

        self.cliente_actual = cliente
        if self.nombre_cliente_txt:
            self.nombre_cliente_txt.setText(cliente.nombre)
        if self.direccion_cliente_txt:
            self.direccion_cliente_txt.setText(cliente.direccion or "")
        if self.email_cliente_txt:
            self.email_cliente_txt.setText(cliente.email or "")
        if self.telefono_cliente_txt:
            self.telefono_cliente_txt.setText(cliente.telefono or "")

    def _agregar_detalle(self):
        if not self.tabla_productos or not self.tabla_productos.selectionModel():
            return
        filas = self.tabla_productos.selectionModel().selectedRows()
        if not filas:
            QMessageBox.information(self, "Seleccione", "Seleccione un producto para agregar al detalle.")
            return
        fila = filas[0].row()
        producto_id = int(self.tabla_productos.item(fila, 0).text())
        producto = self.productos_por_id.get(producto_id)
        if not producto:
            return

        if producto.stock is not None and producto.stock <= 0:
            QMessageBox.information(self, "Sin stock", "El producto seleccionado no tiene stock disponible.")
            return

        cantidad, ok = QInputDialog.getInt(
            self,
            "Cantidad",
            f"Ingrese la cantidad para {producto.nombre}",
            1,
            1,
            max(producto.stock, 1000) if producto.stock else 1000,
        )
        if not ok:
            return

        if producto.stock is not None and producto.stock < cantidad:
            QMessageBox.warning(self, "Stock insuficiente", "La cantidad excede el stock disponible.")
            return

        existente = next((d for d in self.detalles if d["id_producto"] == producto.id_producto), None)
        if existente:
            nueva_cantidad = existente["cantidad"] + cantidad
            if producto.stock is not None and nueva_cantidad > producto.stock:
                QMessageBox.warning(self, "Stock insuficiente", "No puede superar el stock disponible.")
                return
            existente["cantidad"] = nueva_cantidad
            existente["subtotal"] = nueva_cantidad * producto.valor_venta
        else:
            self.detalles.append(
                {
                    "id_producto": producto.id_producto,
                    "nombre": producto.nombre,
                    "cantidad": cantidad,
                    "precio": producto.valor_venta,
                    "subtotal": cantidad * producto.valor_venta,
                }
            )
        self._refrescar_detalle()

    def _eliminar_detalle(self):
        if not self.tabla_detalle or not self.tabla_detalle.selectionModel():
            return
        filas = self.tabla_detalle.selectionModel().selectedRows()
        if not filas:
            return
        fila = filas[0].row()
        producto_id = int(self.tabla_detalle.item(fila, 0).text())
        self.detalles = [d for d in self.detalles if d["id_producto"] != producto_id]
        self._refrescar_detalle()

    def _refrescar_detalle(self):
        if not self.tabla_detalle:
            return
        self.tabla_detalle.setRowCount(len(self.detalles))
        for fila, detalle in enumerate(self.detalles):
            datos = [
                detalle["id_producto"],
                detalle["nombre"],
                detalle["cantidad"],
                f"{detalle['precio']:.2f}",
                f"{detalle['subtotal']:.2f}",
            ]
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabla_detalle.setItem(fila, col, item)
        self.tabla_detalle.resizeColumnsToContents()
        self._actualizar_total()

    def _actualizar_total(self):
        total = sum(detalle["subtotal"] for detalle in self.detalles)
        if self.total_txt:
            self.total_txt.setText(f"{total:.2f}")

    def _registrar_venta(self):
        if not self.cliente_actual:
            QMessageBox.warning(self, "Cliente requerido", "Busque y seleccione un cliente antes de registrar la venta.")
            return
        if not self.detalles:
            QMessageBox.warning(self, "Detalle requerido", "Agregue al menos un producto al detalle.")
            return

        fecha_venta = self.fecha_edit.date().toPython() if self.fecha_edit else datetime.now().date()
        tipo_pago = "Credito" if self.credito_btn and self.credito_btn.isChecked() else "Contado"
        total = float(self.total_txt.text() or 0)

        if total <= 0:
            QMessageBox.warning(self, "Total inválido", "El total de la venta debe ser mayor a cero.")
            return

        venta = Venta(
            id_cliente=self.cliente_actual.id_cliente,
            fecha=fecha_venta,
            tipo_pago=tipo_pago,
            total=total,
            id_usuario=getattr(self.usuario, "id_usuario", None),
            estado="Registrada",
        )

        if venta.id_usuario is None:
            QMessageBox.warning(self, "Usuario requerido", "No se pudo determinar el usuario autenticado.")
            return

        meses = None
        cuota_inicial = 0.0
        saldo_financiado = 0.0
        interes_aplicado = 0.05

        if tipo_pago == "Credito":
            if CreditoDAO.cliente_tiene_credito_activo(self.cliente_actual.id_cliente):
                QMessageBox.warning(
                    self,
                    "Crédito pendiente",
                    "El cliente seleccionado tiene un crédito activo o en mora. "
                    "Debe liquidarlo antes de solicitar uno nuevo.",
                )
                return

            cuota_inicial = round(total * 0.30, 2)
            saldo_base = total * 0.70
            saldo_financiado = round(saldo_base * (1 + interes_aplicado), 2)

            if saldo_financiado <= 0:
                QMessageBox.warning(self, "Datos inválidos", "El saldo a financiar debe ser mayor que cero.")
                return

            meses_opciones = ["12", "18", "24"]
            meses_texto, ok_meses = QInputDialog.getItem(
                self,
                "Número de cuotas",
                (
                    "Seleccione el número de cuotas permitidas (12, 18 o 24).\n\n"
                    "Recuerde: cuota inicial 30% y el saldo (70%) se financia con un 5% de interés."
                ),
                meses_opciones,
                0,
                False,
            )
            if not ok_meses or not meses_texto:
                QMessageBox.information(self, "Operación cancelada", "No se seleccionó el número de cuotas.")
                return
            meses = int(meses_texto)

        venta_id = None
        credito_id = None
        try:
            venta_id = VentaDAO.agregar(venta)
            for detalle in self.detalles:
                producto = self.productos_por_id.get(detalle["id_producto"])
                if producto and producto.stock is not None and detalle["cantidad"] > producto.stock:
                    raise ValueError(f"El producto {producto.nombre} no tiene stock suficiente.")
                detalle_modelo = DetalleVenta(
                    id_venta=venta_id,
                    id_producto=detalle["id_producto"],
                    cantidad=detalle["cantidad"],
                    precio_unitario=detalle["precio"],
                    subtotal=detalle["subtotal"],
                )
                DetalleVentaDAO.agregar(detalle_modelo)
                if producto and producto.stock is not None:
                    nuevo_stock = producto.stock - detalle["cantidad"]
                    ProductoDAO.actualizar_stock(producto.id_producto, nuevo_stock)
                    producto.stock = nuevo_stock

            if tipo_pago == "Credito":
                credito = Credito(
                    id_venta=venta_id,
                    cuota_inicial=cuota_inicial,
                    saldo=saldo_financiado,
                    meses=meses,
                    interes=interes_aplicado,
                    estado="Activo",
                )
                credito_id = CreditoDAO.crear(credito)

                cuotas = self._generar_cuotas(credito_id, fecha_venta, meses, saldo_financiado)
                for cuota in cuotas:
                    CuotaDAO.crear(cuota)

            QMessageBox.information(
                self,
                "Éxito",
                "Venta registrada correctamente.\n"
                + (
                    f"Crédito generado: cuota inicial $ {cuota_inicial:.2f}, "
                    f"{meses} cuotas sobre $ {saldo_financiado:.2f}."
                    if tipo_pago == "Credito"
                    else ""
                ),
            )
            if venta_id:
                self._mostrar_factura(venta_id)
            self._reiniciar_formulario()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo registrar la venta:\n{error}")
            if venta_id:
                try:
                    DetalleVentaDAO.eliminar_por_venta(venta_id)
                    if credito_id:
                        CuotaDAO.eliminar_por_credito(credito_id)
                        CreditoDAO.eliminar(credito_id)
                    VentaDAO.eliminar(venta_id)
                except Exception:
                    pass

    def _generar_cuotas(self, id_credito: int, fecha_base, meses: int, monto_total: float):
        cuotas = []
        fecha_dt = datetime.combine(fecha_base, datetime.min.time()) if isinstance(fecha_base, datetime) else datetime(fecha_base.year, fecha_base.month, fecha_base.day)
        if meses <= 0:
            return cuotas

        cuota_base = round(monto_total / meses, 2)
        acumulado = 0.0
        for i in range(1, meses + 1):
            fecha_programada = self._sumar_meses(fecha_dt, i)
            valor_programado = cuota_base
            if i == meses:
                valor_programado = round(monto_total - acumulado, 2)
            acumulado += valor_programado
            cuotas.append(
                Cuota(
                    id_credito=id_credito,
                    numero=i,
                    fecha_programada=fecha_programada.date(),
                    valor_programado=valor_programado,
                    valor_pagado=0.0,
                    fecha_pago=None,
                    estado="Pendiente",
                )
            )
        return cuotas

    @staticmethod
    def _sumar_meses(fecha: datetime, meses: int) -> datetime:
        anio = fecha.year + (fecha.month - 1 + meses) // 12
        mes = (fecha.month - 1 + meses) % 12 + 1
        dia = min(fecha.day, RegistrarVentaController._dias_en_mes(anio, mes))
        return datetime(anio, mes, dia)

    @staticmethod
    def _dias_en_mes(anio: int, mes: int) -> int:
        if mes in (1, 3, 5, 7, 8, 10, 12):
            return 31
        if mes in (4, 6, 9, 11):
            return 30
        bisiesto = (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)
        return 29 if bisiesto else 28

    def _mostrar_factura(self, venta_id: int) -> None:
        try:
            datos = generar_datos_factura(venta_id)
        except Exception as error:
            QMessageBox.warning(self, "Factura", f"No se pudo generar la factura:\n{error}")
            return

        dialogo = FacturaDialog(datos, self)
        dialogo.show()
        self._facturas_emitidas.append(dialogo)

        def _limpiar_referencia(obj=None, dlg=dialogo):
            if dlg in self._facturas_emitidas:
                self._facturas_emitidas.remove(dlg)

        dialogo.destroyed.connect(_limpiar_referencia)

    def _reiniciar_formulario(self):
        self.cliente_actual = None
        self.detalles = []
        self._refrescar_detalle()
        if self.cedula_txt:
            self.cedula_txt.clear()
        for campo in [self.nombre_cliente_txt, self.direccion_cliente_txt, self.email_cliente_txt, self.telefono_cliente_txt]:
            if campo:
                campo.clear()
        if self.fecha_edit:
            self.fecha_edit.setDate(QDate.currentDate())
        if self.contado_btn:
            self.contado_btn.setChecked(True)
        if self.total_txt:
            self.total_txt.clear()
        self._cargar_productos()