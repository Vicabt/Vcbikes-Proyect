-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS DBvcbikes;
USE DBvcbikes;

-- Tabla Cliente
CREATE TABLE Cliente (
    ID_Cliente INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Identificación VARCHAR(50) UNIQUE NOT NULL,
    Dirección TEXT NOT NULL,
    Teléfono VARCHAR(20) NOT NULL,
    Correo_Electrónico VARCHAR(100) UNIQUE NOT NULL
);

-- Tabla Proveedor
CREATE TABLE Proveedor (
    ID_Proveedor INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Contacto VARCHAR(100),
    Teléfono VARCHAR(20) NOT NULL,
    Correo_Electrónico VARCHAR(100) UNIQUE NOT NULL,
    Dirección TEXT NOT NULL
);

-- Tabla Producto
CREATE TABLE Producto (
    ID_Producto INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Descripción TEXT,
    Categoría ENUM('Motocicleta', 'Repuesto', 'Accesorio') NOT NULL,
    Precio DECIMAL(10,2) NOT NULL CHECK (Precio >= 0),
    Stock_Disponible INT NOT NULL CHECK (Stock_Disponible >= 0),
    ID_Proveedor INT NOT NULL,
    FOREIGN KEY (ID_Proveedor) REFERENCES Proveedor(ID_Proveedor) ON DELETE CASCADE
);

-- Tabla Motocicleta_Cliente
CREATE TABLE Motocicleta_Cliente (
    ID_Motocicleta INT AUTO_INCREMENT PRIMARY KEY,
    ID_Cliente INT NOT NULL,
    Marca VARCHAR(50) NOT NULL,
    Modelo VARCHAR(50) NOT NULL,
    Año INT NOT NULL CHECK (Año >= 1900),
    Número_Serie VARCHAR(50) UNIQUE NOT NULL,
    Placa VARCHAR(20) UNIQUE NOT NULL,
    Fecha_Registro DATE NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Cliente(ID_Cliente) ON DELETE CASCADE
);

-- Tabla Seguro_Motocicleta
CREATE TABLE Seguro_Motocicleta (
    ID_Seguro INT AUTO_INCREMENT PRIMARY KEY,
    ID_Motocicleta INT NOT NULL,
    Aseguradora VARCHAR(100) NOT NULL,
    Número_Póliza VARCHAR(50) UNIQUE NOT NULL,
    Fecha_Inicio DATE NOT NULL,
    Fecha_Vencimiento DATE NOT NULL,
    Cobertura TEXT NOT NULL,
    Estado ENUM('Vigente', 'Vencido') NOT NULL,
    FOREIGN KEY (ID_Motocicleta) REFERENCES Motocicleta_Cliente(ID_Motocicleta) ON DELETE CASCADE
);

-- Tabla Garantía_Motocicleta
CREATE TABLE Garantía_Motocicleta (
    ID_Garantía INT AUTO_INCREMENT PRIMARY KEY,
    ID_Motocicleta INT NOT NULL,
    Fecha_Inicio DATE NOT NULL,
    Fecha_Vencimiento DATE NOT NULL,
    Cobertura TEXT NOT NULL,
    Condiciones TEXT NOT NULL,
    Estado ENUM('Vigente', 'Expirada') NOT NULL,
    FOREIGN KEY (ID_Motocicleta) REFERENCES Motocicleta_Cliente(ID_Motocicleta) ON DELETE CASCADE
);

-- Tabla Compra
CREATE TABLE Compra (
    ID_Compra INT AUTO_INCREMENT PRIMARY KEY,
    ID_Cliente INT NOT NULL,
    Fecha_Compra DATE NOT NULL,
    Total DECIMAL(10,2) NOT NULL CHECK (Total >= 0),
    Método_Pago VARCHAR(50) NOT NULL,
    Estado ENUM('Completada', 'Pendiente', 'Cancelada') NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Cliente(ID_Cliente) ON DELETE CASCADE
);

-- Tabla Detalle_Compra
CREATE TABLE Detalle_Compra (
    ID_Detalle INT AUTO_INCREMENT PRIMARY KEY,
    ID_Compra INT NOT NULL,
    ID_Producto INT NOT NULL,
    Cantidad INT NOT NULL CHECK (Cantidad > 0),
    Precio_Unitario DECIMAL(10,2) NOT NULL CHECK (Precio_Unitario >= 0),
    Subtotal DECIMAL(10,2) NOT NULL CHECK (Subtotal >= 0),
    FOREIGN KEY (ID_Compra) REFERENCES Compra(ID_Compra) ON DELETE CASCADE,
    FOREIGN KEY (ID_Producto) REFERENCES Producto(ID_Producto) ON DELETE CASCADE
);

-- Tabla Inventario
CREATE TABLE Inventario (
    ID_Inventario INT AUTO_INCREMENT PRIMARY KEY,
    ID_Producto INT NOT NULL,
    Cantidad_Stock INT NOT NULL CHECK (Cantidad_Stock >= 0),
    Ubicación_Almacén TEXT NOT NULL,
    Estado ENUM('Disponible', 'Bajo Stock', 'Agotado') NOT NULL,
    FOREIGN KEY (ID_Producto) REFERENCES Producto(ID_Producto) ON DELETE CASCADE
);

-- Tabla Mantenimiento
CREATE TABLE Mantenimiento (
    ID_Mantenimiento INT AUTO_INCREMENT PRIMARY KEY,
    ID_Cliente INT NOT NULL,
    ID_Motocicleta INT NOT NULL,
    Tipo_Mantenimiento ENUM('Preventivo', 'Correctivo') NOT NULL,
    Fecha_Programada DATE NOT NULL,
    Fecha_Realización DATE,
    Descripción TEXT NOT NULL,
    Costo DECIMAL(10,2) NOT NULL CHECK (Costo >= 0),
    Estado ENUM('Pendiente', 'Completado', 'Cancelado') NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Cliente(ID_Cliente) ON DELETE CASCADE,
    FOREIGN KEY (ID_Motocicleta) REFERENCES Motocicleta_Cliente(ID_Motocicleta) ON DELETE CASCADE
);

-- Tabla Reparación
CREATE TABLE Reparación (
    ID_Reparación INT AUTO_INCREMENT PRIMARY KEY,
    ID_Motocicleta INT NULL,
    ID_Producto INT NULL,
    Fecha_Ingreso DATE NOT NULL,
    Fecha_Salida DATE,
    Diagnóstico TEXT NOT NULL,
    Repuestos_Utilizados TEXT,
    Costo_Total DECIMAL(10,2) NOT NULL CHECK (Costo_Total >= 0),
    Estado ENUM('Pendiente', 'En reparación', 'Finalizado') NOT NULL,
    FOREIGN KEY (ID_Motocicleta) REFERENCES Motocicleta_Cliente(ID_Motocicleta) ON DELETE SET NULL,
    FOREIGN KEY (ID_Producto) REFERENCES Producto(ID_Producto) ON DELETE SET NULL
);

-- Tabla Servicio_Postventa
CREATE TABLE Servicio_Postventa (
    ID_Servicio INT AUTO_INCREMENT PRIMARY KEY,
    ID_Cliente INT NOT NULL,
    ID_Motocicleta INT NULL,
    Descripción TEXT NOT NULL,
    Fecha_Solicitud DATE NOT NULL,
    Fecha_Entrega DATE,
    Costo DECIMAL(10,2) NOT NULL CHECK (Costo >= 0),
    Estado ENUM('Pendiente', 'En proceso', 'Completado') NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Cliente(ID_Cliente) ON DELETE CASCADE,
    FOREIGN KEY (ID_Motocicleta) REFERENCES Motocicleta_Cliente(ID_Motocicleta) ON DELETE SET NULL
);

-- Tabla Garantía_Producto
CREATE TABLE Garantía_Producto (
    ID_Garantía INT AUTO_INCREMENT PRIMARY KEY,
    ID_Producto INT NOT NULL,
    Fecha_Inicio DATE NOT NULL,
    Fecha_Fin DATE NOT NULL,
    Condiciones TEXT NOT NULL,
    Estado ENUM('Activa', 'Expirada', 'Rechazada', 'Aprobada') NOT NULL,
    FOREIGN KEY (ID_Producto) REFERENCES Producto(ID_Producto) ON DELETE CASCADE
);

-- Tabla Notificación
CREATE TABLE Notificación (
    ID_Notificación INT AUTO_INCREMENT PRIMARY KEY,
    ID_Cliente INT NOT NULL,
    ID_Mantenimiento INT NULL,
    Mensaje TEXT NOT NULL,
    Fecha_Programada DATE NOT NULL,
    Estado ENUM('Pendiente', 'Enviada', 'Vencida') NOT NULL,
    Tipo ENUM('Correo', 'SMS', 'WhatsApp', 'Notificación en App/Web') NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Cliente(ID_Cliente) ON DELETE CASCADE,
    FOREIGN KEY (ID_Mantenimiento) REFERENCES Mantenimiento(ID_Mantenimiento) ON DELETE SET NULL
);

-- Tabla Preferencias_Notificación
CREATE TABLE Preferencias_Notificación (
    ID_Cliente INT PRIMARY KEY,
    Canal_Preferido ENUM('Correo', 'SMS', 'WhatsApp', 'Notificación en App/Web') NOT NULL,
    Frecuencia ENUM('Inmediata', 'Diaria', 'Semanal') NOT NULL,
    Estado ENUM('Activo', 'Desactivado') NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Cliente(ID_Cliente) ON DELETE CASCADE
);
