from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import inspect

db = SQLAlchemy()


# Modelo de Categoria
class Categoria(db.Model):
    descripcion = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado
    # Relación con productos
    productos = db.relationship('Producto', back_populates='categoria_parent', lazy=True, primaryjoin="Categoria.id == Producto.categoria_id")
    # Relación con subcategorías
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True)

    def __repr__(self):
        return f"Categoria('{self.nombre}')"


# Modelo de Cliente
class Cliente(db.Model):
    direccion = db.Column(db.String(200))
    documento_identidad = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado
    # Relación con ventas
    ventas = db.relationship('Venta', backref='cliente', lazy=True)

    def __repr__(self):
        return f"Cliente('{self.nombre}')"


# Modelo de DetalleVenta
class DetalleVenta(db.Model):
    cantidad = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado

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
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado

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
    subcategoria_parent = db.relationship('Subcategoria', back_populates='productos',  primaryjoin="Subcategoria.id == Producto.subcategoria_id")
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=True)
    categoria_parent = db.relationship('Categoria', back_populates='productos', primaryjoin="Categoria.id == Producto.categoria_id")
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado

    def __repr__(self):
        return f"Producto('{self.nombre}', ${self.precio}, Stock: {self.stock})"


# Modelo de Proveedor
class Proveedor(db.Model):
    contacto = db.Column(db.String(100))
    descripcion = db.Column(db.Text, nullable = True)
    direccion = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship('Producto', back_populates='proveedor', lazy=True)
    telefono = db.Column(db.String(20))
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado

    def __repr__(self):
        return f"Proveedor('{self.nombre}')"


# Modelo de Subcategoria
class Subcategoria(db.Model):
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    descripcion = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship('Producto', back_populates='subcategoria_parent', lazy=True, primaryjoin="Subcategoria.id == Producto.subcategoria_id")
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado

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
    estado = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado
    rol = db.Column(db.String(20), default='empleado')  # Valores: 'administrador', 'empleado'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    total = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=0.19)  # 19% IVA por defecto
    descuento = db.Column(db.Float, default=0.0)
    descuento_porcentaje = db.Column(db.Float, default=0.0)
    numero_factura = db.Column(db.String(50), unique=True)
    estado = db.Column(db.String(20), default='pendiente')
    estado_registro = db.Column(db.Integer, default=0)  # 0 = activo, 1 = eliminado
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    metodo_pago = db.Column(db.String(50), default='efectivo')
    notas = db.Column(db.Text)
    # Relación con Producto
    producto = db.relationship('Producto', backref='ventas')

    def __repr__(self):
        return f"Venta(ID: {self.id}, Factura: {self.numero_factura}, Total: ${self.total})"

    def calcular_total(self):
        """Calcula el total de la venta incluyendo IVA y descuentos"""
        # Asegurarnos de que todos los valores numéricos estén inicializados
        if self.subtotal is None:
            self.subtotal = 0.0
        
        if self.descuento is None:
            self.descuento = 0.0
            
        if self.descuento_porcentaje is None:
            self.descuento_porcentaje = 0.0
            
        if self.iva is None:
            self.iva = 0.19  # Valor por defecto si es None
            
        if self.total is None:
            self.total = 0.0
        
        # Verificar que producto exista antes de acceder a su precio
        if self.producto is None:
            # Si no hay producto, buscar el producto directamente
            if inspect(self).session:
                self.producto = inspect(self).session.query(Producto).get(self.producto_id)
        
        # Si aún no hay producto, establecer valores predeterminados
        if self.producto is None:
            self.subtotal = 0.0
            self.descuento = 0.0
            self.total = 0.0
            return self.total
            
        # Continuar con el cálculo normal
        try:
            # Asegurarse de que el precio es un número
            precio = float(self.producto.precio) if self.producto.precio is not None else 0.0
            self.subtotal = precio  # Precio base del producto
            
            # Aplicar descuento si existe
            if self.descuento_porcentaje > 0:
                self.descuento = self.subtotal * (self.descuento_porcentaje / 100)
            
            # Calcular IVA sobre el monto después del descuento
            monto_despues_descuento = self.subtotal - self.descuento
            iva_monto = monto_despues_descuento * self.iva
            
            # Calcular total final
            self.total = monto_despues_descuento + iva_monto
            return self.total
        except (TypeError, ValueError) as e:
            # En caso de error, establecer valores seguros
            self.subtotal = 0.0
            self.descuento = 0.0
            self.total = 0.0
            return self.total