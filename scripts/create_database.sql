IF DB_ID('VentasElectrodomesticos') IS NULL
BEGIN
    CREATE DATABASE VentasElectrodomesticos;
END;
GO

USE VentasElectrodomesticos;
GO

IF OBJECT_ID('dbo.Cuota', 'U') IS NOT NULL DROP TABLE dbo.Cuota;
IF OBJECT_ID('dbo.Credito', 'U') IS NOT NULL DROP TABLE dbo.Credito;
IF OBJECT_ID('dbo.DetalleVenta', 'U') IS NOT NULL DROP TABLE dbo.DetalleVenta;
IF OBJECT_ID('dbo.Venta', 'U') IS NOT NULL DROP TABLE dbo.Venta;
IF OBJECT_ID('dbo.Producto', 'U') IS NOT NULL DROP TABLE dbo.Producto;
IF OBJECT_ID('dbo.Categoria', 'U') IS NOT NULL DROP TABLE dbo.Categoria;
IF OBJECT_ID('dbo.Cliente', 'U') IS NOT NULL DROP TABLE dbo.Cliente;
IF OBJECT_ID('dbo.Bitacora', 'U') IS NOT NULL DROP TABLE dbo.Bitacora;
IF OBJECT_ID('dbo.Usuario', 'U') IS NOT NULL DROP TABLE dbo.Usuario;
GO

CREATE TABLE dbo.Usuario (
    id_usuario      INT IDENTITY(1,1) PRIMARY KEY,
    cedula          NVARCHAR(20) NOT NULL UNIQUE,
    nombre          NVARCHAR(100) NOT NULL,
    email           NVARCHAR(150) NOT NULL,
    rol             INT NOT NULL,
    estado          NVARCHAR(20) NOT NULL DEFAULT 'Activo',
    password_hash   VARBINARY(64) NOT NULL,
    fecha_creacion  DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
    ultimo_acceso   DATETIME2(0) NULL
);

CREATE TABLE dbo.Categoria (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nombre       NVARCHAR(50) NOT NULL UNIQUE,
    iva          DECIMAL(5,2) NOT NULL,
    utilidad     DECIMAL(5,2) NOT NULL
);

CREATE TABLE dbo.Cliente (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre     NVARCHAR(120) NOT NULL,
    cedula     NVARCHAR(20)  NOT NULL UNIQUE,
    direccion  NVARCHAR(150) NULL,
    telefono   NVARCHAR(20)  NULL,
    correo     NVARCHAR(120) NULL
);

CREATE TABLE dbo.Producto (
    id_producto        INT IDENTITY(1,1) PRIMARY KEY,
    codigo             NVARCHAR(30) NOT NULL UNIQUE,
    nombre             NVARCHAR(120) NOT NULL,
    id_categoria       INT NOT NULL REFERENCES dbo.Categoria(id_categoria),
    valor_adquisicion  DECIMAL(18,2) NOT NULL,
    valor_venta        DECIMAL(18,2) NOT NULL,
    stock              INT NOT NULL DEFAULT 0
);

CREATE TABLE dbo.Venta (
    id_venta    INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente  INT NOT NULL REFERENCES dbo.Cliente(id_cliente),
    fecha       DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
    tipo        NVARCHAR(20) NOT NULL,
    total       DECIMAL(18,2) NOT NULL,
    id_usuario  INT NOT NULL REFERENCES dbo.Usuario(id_usuario),
    estado      NVARCHAR(20) NOT NULL DEFAULT 'Registrada'
);

CREATE TABLE dbo.DetalleVenta (
    id_detalle     INT IDENTITY(1,1) PRIMARY KEY,
    id_venta       INT NOT NULL REFERENCES dbo.Venta(id_venta),
    id_producto    INT NOT NULL REFERENCES dbo.Producto(id_producto),
    cantidad       INT NOT NULL,
    precio_unitario DECIMAL(18,2) NOT NULL,
    subtotal       AS CAST(cantidad * precio_unitario AS DECIMAL(18,2))
);

CREATE TABLE dbo.Credito (
    id_credito    INT IDENTITY(1,1) PRIMARY KEY,
    id_venta      INT NOT NULL UNIQUE REFERENCES dbo.Venta(id_venta),
    cuota_inicial DECIMAL(18,2) NOT NULL,
    saldo         DECIMAL(18,2) NOT NULL,
    meses         INT NOT NULL,
    interes       DECIMAL(5,2) NOT NULL,
    estado        NVARCHAR(20) NOT NULL DEFAULT 'Activo'
);

CREATE TABLE dbo.Cuota (
    id_cuota          INT IDENTITY(1,1) PRIMARY KEY,
    id_credito        INT NOT NULL REFERENCES dbo.Credito(id_credito),
    numero            INT NOT NULL,
    fecha_programada  DATE NOT NULL,
    valor_programado  DECIMAL(18,2) NOT NULL,
    valor_pagado      DECIMAL(18,2) NOT NULL DEFAULT 0,
    fecha_pago        DATE NULL,
    estado            NVARCHAR(20) NOT NULL DEFAULT 'Pendiente'
);

CREATE UNIQUE INDEX IX_Cuota_Credito_Numero ON dbo.Cuota(id_credito, numero);

CREATE TABLE dbo.Bitacora (
    id_bitacora INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario  INT NOT NULL REFERENCES dbo.Usuario(id_usuario),
    tipo_evento NVARCHAR(50) NOT NULL,
    detalle     NVARCHAR(250) NULL,
    fecha_hora  DATETIME2(0) NOT NULL DEFAULT SYSDATETIME()
);

PRINT 'Base de datos y tablas creadas correctamente.';
GO


