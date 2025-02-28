from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'Cliente'
    id = db.Column('ID_Cliente', db.Integer, primary_key=True)
    nombre = db.Column('Nombre', db.String(100), nullable=False)
    identificacion = db.Column('Identificación', db.String(50), unique=True, nullable=False)
    direccion = db.Column('Dirección', db.Text, nullable=False)
    telefono = db.Column('Teléfono', db.String(20), nullable=False)
    correo_electronico = db.Column('Correo_Electrónico', db.String(100), unique=True, nullable=False)

class Proveedor(db.Model):
    __tablename__ = 'Proveedor'
    id = db.Column('ID_Proveedor', db.Integer, primary_key=True)
    nombre = db.Column('Nombre', db.String(100), nullable=False)
    contacto = db.Column('Contacto', db.String(100))
    telefono = db.Column('Teléfono', db.String(20), nullable=False)
    correo_electronico = db.Column('Correo_Electrónico', db.String(100), unique=True, nullable=False)
    direccion = db.Column('Dirección', db.Text, nullable=False)

class Producto(db.Model):
    __tablename__ = 'Producto'
    id = db.Column('ID_Producto', db.Integer, primary_key=True)
    nombre = db.Column('Nombre', db.String(100), nullable=False)
    descripcion = db.Column('Descripción', db.Text)
    categoria = db.Column('Categoría', db.Enum('Motocicleta', 'Repuesto', 'Accesorio'), nullable=False)
    precio = db.Column('Precio', db.Float, nullable=False)
    stock = db.Column('Stock', db.Integer, nullable=False)
    imagen = db.Column('Imagen', db.String(255))

class Venta(db.Model):
    __tablename__ = 'Venta'
    id = db.Column('ID_Venta', db.Integer, primary_key=True)
    fecha = db.Column('Fecha', db.DateTime, nullable=False)
    total = db.Column('Total', db.Float, nullable=False)
    cliente_id = db.Column('ID_Cliente', db.Integer, db.ForeignKey('Cliente.ID_Cliente'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('ventas', lazy=True))

class DetalleVenta(db.Model):
    __tablename__ = 'DetalleVenta'
    id = db.Column('ID_Detalle', db.Integer, primary_key=True)
    venta_id = db.Column('ID_Venta', db.Integer, db.ForeignKey('Venta.ID_Venta'), nullable=False)
    producto_id = db.Column('ID_Producto', db.Integer, db.ForeignKey('Producto.ID_Producto'), nullable=False)
    cantidad = db.Column('Cantidad', db.Integer, nullable=False)
    precio_unitario = db.Column('Precio_Unitario', db.Float, nullable=False)
    venta = db.relationship('Venta', backref=db.backref('detalles', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('detalles', lazy=True))
