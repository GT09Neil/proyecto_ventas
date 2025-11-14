# Guía del Proyecto “Sistema de Ventas de Electrodomésticos”

## 1. Contexto y Propósito

El proyecto desarrolla una aplicación de escritorio en **Python** con interfaz **PySide6** y base de datos **SQL Server** para automatizar la operación de una tienda de electrodomésticos.  
Los objetivos principales son:

- Aplicar los conceptos de modelado, normalización, consultas SQL, reportes y auditoría vistos en el curso.
- Utilizar un lenguaje de programación para construir la GUI y un SGBD real para persistir la información.
- Implementar control de acceso por niveles de usuario y trazar el ingreso/salida mediante bitácora.

## 2. Diseño de Base de Datos

- **Entidades / Tablas principales:** `Cliente`, `Producto`, `Categoria`, `Venta`, `DetalleVenta`, `Usuario`, `Credito`, `Cuota`, `Bitacora`, entre otras (más de 10 tablas).
- **Relaciones:**  
  - 1–N: Cliente→Venta, Venta→DetalleVenta, Venta→Credito, Credito→Cuota, Usuario→Venta.  
  - N–N: Productos en ventas a través de `DetalleVenta`.
- **Normalización:** Se aplicaron 1FN, 2FN y 3FN (atributos atómicos, sin dependencias parciales ni transitivas).
- **Entregables pendientes para anexar en PDF:** enunciado aprobado, diagrama ER (Chen), proceso de normalización, diagrama relacional y diccionario de datos (atributos, tipos, restricciones).

## 3. Stack Tecnológico

| Componente | Descripción |
|------------|-------------|
| Lenguaje   | Python 3.11+ |
| GUI        | PySide6 (Qt) |
| SGBD       | SQL Server (ODBC Driver 17) |
| Dependencias clave | `pyodbc`, `PySide6`, `PySide6_Addons`, `PySide6_Essentials` |

## 4. Estructura del Código

- `dao/`: Clases de acceso a datos (CRUD, consultas y operaciones especializadas).
- `modelos/`: Objetos de dominio (Cliente, Producto, Venta, Credito, etc.).
- `Controllers/`: Controladores de la interfaz (CRUDs, reportes, utilidades, autenticación).
- `GUI/`: Formatos `.ui` creados con Qt Designer.
- `reportes/`: Consultas parametrizadas para reportes y consultas avanzadas.
- `main.py`: Punto de entrada de la aplicación (lógica de login inicial).

## 5. Funcionalidades Implementadas

### 5.1 Autenticación y Roles
- Login con cédula y contraseña hasheada (SHA-256).
- Roles definidos:
  - **Administrador:** acceso total a menús y CRUDs.
  - **Paramétrico:** acceso restringido (sin usuarios ni bitácora).
  - **Esporádico:** acceso únicamente a la pestaña de consultas.
- Bitácora de accesos (registra `Login` y `Logout` automáticamente).

### 5.2 CRUDs Disponibles
- Clientes, productos, categorías, ventas, créditos, cuotas, usuarios, bitácora.
- `RegistrarVenta`: busca cliente, arma detalle, registra venta, descuenta stock y genera crédito/cuotas si corresponde.

### 5.3 Reportes (6)
1. Total de ventas por mes (agrega ventas por tipo y unidades vendidas).
2. Clientes morosos (créditos con cuotas vencidas).
3. Inventario por categoría (stock, valor estimado, promedios).
4. Ventas por periodo (resumen por tipo contado/crédito y totales globales).
5. Top clientes por compras (ranking de consumo).
6. IVA trimestral DIAN (base, IVA generado y total por categoría).

### 5.4 Consultas (5)
1. Ventas por cliente.
2. Productos con stock crítico.
3. Créditos activos con saldo.
4. Cuotas vencidas.
5. Ventas por usuario.

### 5.5 Utilidades
- Calculadora (llama al ejecutable del sistema).
- Calendario interactivo interno.
- Gestión de usuarios (CRUD con validación de único administrador).
- Bitácora de accesos.
- Pestaña `Ayudas` con manual de uso integrado y datos de soporte.
- Generación de factura de venta en ventana adicional con opción de exportar a PDF (se abre automáticamente al registrar una venta).

## 6. Inicialización Automática de Datos

- La clase `DataInitializer` (ver `data_initializer.py`) revisa la base de datos al iniciar la aplicación.
- Si detecta tablas vacías, crea automáticamente:
  - Categorías base (Audio, Video, Tecnología, Cocina).
  - Usuario administrador (`cedula`: **9999999999**, `password`: **Admin*123**).
  - Cliente de demostración y producto de ejemplo (para pruebas rápidas).
- Los mensajes de advertencia se imprimen en consola si ocurre algún problema durante la carga.

## 7. Flujo de Uso

1. **Iniciar la aplicación**: `main.py` ejecuta el inicializador de datos y luego abre la ventana de login.
2. **Ingresar credenciales**:
   - Cuenta por defecto tras una instalación limpia: `9999999999 / Admin*123`.
   - Cambiar la contraseña desde el CRUD de usuarios después del primer ingreso.
3. **Gestionar información**:
   - `Entidades`: CRUD de clientes, productos, categorías.
   - `Transacciones`: `RegistrarVenta`, créditos, cuotas.
4. **Registrar ventas**:
   - Seleccionar cliente y productos.
   - Si la venta es a crédito, el sistema aplica cuota inicial del 30 %, financia el 70 % con 5 % de interés y genera el plan de 12/18/24 cuotas.
   - Se abre una factura imprimible/exportable en PDF al finalizar.
5. **Consultar información**:
   - `Reportes`: totales mensuales, morosidad, inventario, ventas por periodo, top clientes, IVA trimestral.
   - `Consultas`: ventas por cliente, stock crítico, créditos activos, cuotas vencidas, ventas por usuario.
6. **Utilidades adicionales**: calculadora, calendario, bitácora y administración de usuarios según el rol.
7. **Cerrar sesión**: el evento queda registrado en la bitácora de forma automática.

## 8. Guía Rápida de Operación

1. **Preparar entorno**:
   - Instalar dependencias con `pip install -r requirements.txt`.
   - Configurar SQL Server y ODBC (ver `db_connection.py` para cadena de conexión).
2. **Ejecutar la aplicación**:
   - `py main.py`
3. **Verificar datos iniciales**:
   - Comprobar en consola que no se reportan errores del `DataInitializer`.
   - Ingresar con la cuenta por defecto, revisar categorías y el producto de prueba.
4. **Operación diaria**:
   - Registrar nuevas ventas desde `Transacciones`.
   - Generar reportes y consultas según la necesidad del área financiera/ventas.
   - Administrar usuarios y revisar la bitácora desde `Utilidades`.
5. **Respaldos**:
   - Mantener copia de la base de datos SQL Server.
   - Conservar el PDF de factura exportado para clientes a crédito o contado.

## 9. Consideraciones Técnicas

- La aplicación usa `pyodbc` para conectar con SQL Server (ver `db_connection.py`).
- Los reportes/consultas utilizan comandos SQL multi-tabla con agregaciones y filtros.
- Se controla que solo exista un usuario con rol administrador desde `UsuarioDAO`.
- La bitácora se alimenta al iniciar/cerrar sesión, accesible desde la interfaz.
- La rutina `DataInitializer` evita arranques con tablas vacías y puede reutilizarse para resembrar datos mínimos.
- Para validar la integridad del código se puede ejecutar `py -m compileall Controllers dao modelos reportes`.




