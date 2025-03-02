from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# Modelo de Categoria
class Categoria(db.Model):
    descripcion = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    # Relación con productos
    productos = db.relationship('Producto', back_populates='categoria_parent', lazy=True)
    # Relación con subcategorías
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True)

    def __repr__(self):
        return f"Categoria('{self.nombre}')"


# Modelo de Cliente
class Cliente(db.Model):
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    documento_identidad = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    # Relación con ventas
    ventas = db.relationship('Venta', backref='cliente', lazy=True)

    def __repr__(self):
        return f"Cliente('{self.nombre} {self.apellido}')"


# Modelo de DetalleVenta
class DetalleVenta(db.Model):
    cantidad = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)

    def __repr__(self):
        return f"DetalleVenta(Venta: {self.venta_id}, Producto: {self.producto_id}, Cantidad: {self.cantidad})"


# Modelo de Empleado
class Empleado(db.Model):
    activo = db.Column(db.Boolean, default=True)
    cargo = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(120))
    documento_identidad = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    fecha_contratacion = db.Column(db.Date)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))

    def __repr__(self):
        return f"Empleado('{self.nombre}', '{self.cargo}', '{self.email}')"


# Modelo de Producto
class Producto(db.Model):
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    codigo = db.Column(db.String(50), unique=True)
    descripcion = db.Column(db.Text)
    detalles_venta = db.relationship('DetalleVenta', backref='producto', lazy=True)
    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.String(200))  # Ruta a la imagen
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    proveedor = db.relationship('Proveedor', back_populates='productos')
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=True)
    stock = db.Column(db.Integer, default=0)
    subcategoria_parent = db.relationship('Subcategoria', back_populates='productos')
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=True)
    categoria_parent = db.relationship('Categoria', back_populates='productos')

    def __repr__(self):
        return f"Producto('{self.nombre}', ${self.precio}, Stock: {self.stock})"


# Modelo de Proveedor
class Proveedor(db.Model):
    contacto = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship('Producto', back_populates='proveedor', lazy=True)
    telefono = db.Column(db.String(20))

    def __repr__(self):
        return f"Proveedor('{self.nombre}')"


# Modelo de Subcategoria
class Subcategoria(db.Model):
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    descripcion = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship('Producto', back_populates='subcategoria_parent', lazy=True, primaryjoin="Subcategoria.id == Producto.subcategoria_id")

    def __repr__(self):
        return f"Subcategoria('{self.nombre}')"


# Modelo de User
class User(db.Model):
    email = db.Column(db.String(120), unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Guarda el hash de la contraseña
    telefono = db.Column(db.String(20))
    username = db.Column(db.String(20), unique=True, nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# Modelo de Venta
class Venta(db.Model):
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Venta(ID: {self.id}, Fecha: {self.fecha}, Total: ${self.total})"