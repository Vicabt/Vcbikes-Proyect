import os
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()
from datetime import datetime
from models import db, User, Empleado, Categoria, Cliente, Subcategoria, Producto, Proveedor, Venta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import logging
from forms import ProductoForm, NuevaVentaForm, ClienteForm
# Crear la aplicación Flask
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_key_for_development')  # Use environment variable
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración para subida de imágenes
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Build database URI from environment variables
db_username = os.environ.get('DB_USERNAME', 'root')
db_password = os.environ.get('DB_PASSWORD', 'root')
db_host = os.environ.get('DB_HOST', 'localhost')
db_name = os.environ.get('DB_NAME', 'db_vcbikes')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)
migrate = Migrate(app, db)  # Inicializa Flask-Migrate

# Configuración de la aplicación para guardar imagenes de los productos
app.config['UPLOAD_FOLDER'] = 'static/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Función para inicializar datos
def initialize_data():
    # Verificar si ya hay datos
    if Categoria.query.count() == 0:
        # Crear categorías de ejemplo
        cat1 = Categoria(nombre="Motocicletas", descripcion="Vehículos de dos ruedas")
        cat2 = Categoria(nombre="Repuestos", descripcion="Piezas y componentes")
        cat3 = Categoria(nombre="Accesorios", descripcion="Complementos para motos y motociclistas")
        
        db.session.add_all([cat1, cat2, cat3])
        db.session.commit()

# Decorator para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder.', 'error')
            logging.warning('Acceso denegado a la ruta protegida. Redirigiendo al login.')  # Log de acceso denegado
            return redirect(url_for('login'))  # Redirige al login si no está autenticado
        logging.info('Acceso permitido a la ruta protegida.')  # Log de acceso permitido
        return f(*args, **kwargs)
    return decorated_function

# Rutas
@app.route('/')
def index():
    return render_template('index.html', show_back_button=False) # No mostramos boton de regreso


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')
        flash('Mensaje enviado con éxito. Nos pondremos en contacto contigo pronto.')
        return redirect(url_for('contacto'))
    return render_template('contacto.html', show_back_button=False) # No mostramos boton de regreso


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()  # Busca el usuario por nombre de usuario

        logging.debug(f'Intento de inicio de sesión para el usuario: {username}')  # Log de intento de inicio de sesión

        if user and user.check_password(password):  # Verifica si el usuario existe y la contraseña es correcta
            session['user_id'] = user.id  # Guarda el ID del usuario en la sesión
            session['user_name'] = user.name  # Guarda el nombre del usuario en la sesión
            flash('Has iniciado sesión exitosamente!', 'success')
            logging.info(f'Usuario {username} ha iniciado sesión exitosamente.')  # Log de éxito
            return redirect(url_for('dashboard'))  # Redirige al dashboard
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            logging.warning(f'Fallo en el inicio de sesión para el usuario: {username}')  # Log de fallo

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        logging.debug('Accediendo a la ruta de registro.')  # Log al inicio de la función de registro
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('nombre') # Obtiene el nombre del formulario
        telefono = request.form.get('telefono')
        confirm_password = request.form.get('confirm_password')

        print(f"Username recibido: {username}")

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('registro.html')

        # Verifica si el usuario o correo ya existen
        user = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first()

        if user:
            flash('El nombre de usuario ya está registrado.', 'error')
            return render_template('registro.html')

        if email_check:
            flash('El correo electrónico ya está registrado.', 'error')
            return render_template('registro.html')

        try:
            # Crea un nuevo usuario
            password_hash = generate_password_hash(password)
            new_user = User(username=username, email=email, name=name, telefono=telefono, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            logging.debug(f'Usuario creado: {new_user.username}, Email: {new_user.email}')  # Log de usuario creado
            logging.debug(f'Hash de contraseña: {new_user.password_hash}')  # Log del hash de la contraseña
            flash('Te has registrado exitosamente! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            error_message = f'Error al registrar el usuario: {str(e)}'
            logging.error(error_message)  # Log del error
            flash(error_message, 'error')
            return render_template('registro.html')

    return render_template('registro.html')

@app.route('/recuperar-password', methods=['GET', 'POST'])
def recuperar_password():
    return render_template('recuperacion.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', show_back_button=False) # No mostramos boton de regreso


@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    session['previous_page'] = url_for('dashboard')
    if request.method == 'POST':
        nombre = request.form.get('category_name')
        descripcion = request.form.get('category_description')

        # Validación básica
        if not nombre:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return redirect(url_for('categorias'))

        try:
            # Crear nueva categoría
            nueva_categoria = Categoria(
                nombre=nombre,
                descripcion=descripcion
            )
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría agregada con éxito!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar la categoría: {str(e)}', 'error')

        return redirect(url_for('categorias'))

    # Obtener todas las categorías de la base de datos
    categorias = Categoria.query.all()
    return render_template('categorias.html', categories=categorias, show_back_button=True)

@app.route('/categorias/editar/<int:category_id>', methods=['GET', 'POST'])
@login_required
def editar_categoria(category_id):
    categoria = Categoria.query.get_or_404(category_id)

    if request.method == 'POST':
        categoria.nombre = request.form.get('category_name')
        categoria.descripcion = request.form.get('category_description')

        # Validación básica
        if not categoria.nombre:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return redirect(url_for('editar_categoria', category_id=category_id))

        try:
            db.session.commit()
            flash('Categoría actualizada con éxito!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la categoría: {str(e)}', 'error')

        return redirect(url_for('categorias'))

    return render_template('editar_categoria.html', category=categoria, show_back_button=True)

@app.route('/categorias/eliminar/<int:category_id>', methods=['POST'])
@login_required
def eliminar_categoria(category_id):
    categoria = Categoria.query.get_or_404(category_id)
    try:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada con éxito!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la categoría: {str(e)}', 'error')

    return redirect(url_for('categorias'))

@app.route('/subcategorias', methods=['GET', 'POST'])
@login_required
def subcategorias():
    session['previous_page'] = url_for('dashboard')
    categorias = Categoria.query.all()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        parent_category = request.form.get('parent_category')
        subcategory_name = request.form.get('subcategory_name')
        subcategory_description = request.form.get('subcategory_description')
        
        # Crear nueva subcategoría
        nueva_subcategoria = Subcategoria(
            nombre=subcategory_name,
            descripcion=subcategory_description,
            categoria_id=parent_category
        )
        
        try:
            db.session.add(nueva_subcategoria)
            db.session.commit()
            flash('Subcategoría agregada con éxito!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar la subcategoría: {str(e)}', 'error')
        
        return redirect(url_for('subcategorias'))
    
    subcategorias = Subcategoria.query.all()
    return render_template('subcategorias.html', categorias=categorias, subcategorias=subcategorias, show_back_button=True)

@app.route('/get_subcategorias/<int:categoria_id>')
@login_required
def get_subcategorias(categoria_id):
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).all()
    subcategorias_dict = [{'id': sub.id, 'nombre': sub.nombre} for sub in subcategorias]
    return jsonify(subcategorias_dict)

@app.route('/configuracion_usuario')
@login_required
def configuracion_usuario():
    return render_template('configuracion_usuario.html')

from datetime import datetime

@app.route('/empleados', methods=['GET', 'POST'])
@login_required
def empleados():
    session['previous_page'] = url_for('dashboard')
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cargo = request.form.get('cargo')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        documento_identidad = request.form.get('employeeDocument')
        direccion = request.form.get('direccion')
        fecha_contratacion_str = request.form.get('contratacion')
        activo = request.form.get('employeeActive') == 'on'  # Verifica si el checkbox está marcado

        # Validación (¡MUY IMPORTANTE!)
        if not nombre or not cargo or not email:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('empleados'))

        try:
            # Convierte la fecha de contratación a un objeto datetime.date
            fecha_contratacion = datetime.strptime(fecha_contratacion_str, '%Y-%m-%d').date()

            nuevo_empleado = Empleado(
                nombre=nombre,
                cargo=cargo,
                email=email,
                telefono=telefono,
                documento_identidad=documento_identidad,
                direccion=direccion,
                fecha_contratacion=fecha_contratacion,
                activo=activo
            )
            db.session.add(nuevo_empleado)
            db.session.commit()
            flash('Empleado agregado con éxito!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar el empleado: {str(e)}', 'error')

        return redirect(url_for('empleados'))

    # Obtener todos los empleados de la base de datos
    empleados = Empleado.query.all()
    return render_template('empleados.html', empleados=empleados, show_back_button=True)

@app.route('/empleados/editar/<int:empleado_id>', methods=['GET', 'POST'])
@login_required
def editar_empleado(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)

    if request.method == 'POST':
        empleado.nombre = request.form.get('nombre')
        empleado.cargo = request.form.get('cargo')
        empleado.email = request.form.get('email')
        empleado.telefono = request.form.get('telefono')
        empleado.documento_identidad = request.form.get('employeeDocument')
        empleado.direccion = request.form.get('direccion')
        fecha_contratacion_str = request.form.get('contratacion')
        empleado.activo = request.form.get('employeeActive') == 'on'

        # Validación (¡MUY IMPORTANTE!)
        if not empleado.nombre or not empleado.cargo or not empleado.email:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('editar_empleado', empleado_id=empleado_id))

        try:
            # Convierte la fecha de contratación a un objeto datetime.date
            empleado.fecha_contratacion = datetime.strptime(fecha_contratacion_str, '%Y-%m-%d').date()

            db.session.commit()
            flash('Empleado actualizado con éxito!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el empleado: {str(e)}', 'error')

        return redirect(url_for('empleados'))

    return render_template('editar_empleado.html', empleado=empleado, show_back_button=True)

@app.route('/empleados/eliminar/<int:empleado_id>', methods=['POST'])
@login_required
def eliminar_empleado(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)
    try:
        db.session.delete(empleado)
        db.session.commit()
        flash('Empleado eliminado con éxito!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el empleado: {str(e)}', 'error')

    return redirect(url_for('empleados'))

from flask import jsonify

@app.route('/get_employee_details/<int:empleado_id>')
@login_required
def get_employee_details(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)
    # Convierte la fecha a string
    fecha_str = empleado.fecha_contratacion.strftime('%Y-%m-%d') if empleado.fecha_contratacion else None
    # Serializa el objeto Empleado a un diccionario
    empleado_dict = {
        'id': empleado.id,
        'nombre': empleado.nombre,
        'cargo': empleado.cargo,
        'email': empleado.email,
        'telefono': empleado.telefono,
        'documento_identidad': empleado.documento_identidad,
        'direccion': empleado.direccion,
        'fecha_contratacion': fecha_str, # Usa la fecha convertida a string
        'activo': empleado.activo
    }
    return jsonify(empleado_dict)

@app.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    form = ClienteForm()  # Crear una instancia del formulario
    clientes = Cliente.query.all()
    if form.validate_on_submit():  # Si el formulario se envía y es válido
        if Cliente.query.filter_by(email=form.email.data).first():
            flash('El email ya está registrado.', 'error')
            return render_template('clientes.html', form=form, clientes=clientes, show_back_button=True)

        nuevo_cliente = Cliente(
            nombre=form.nombre.data,
            email=form.email.data,
            telefono=form.telefono.data,
            documento_identidad=form.documento_identidad.data,
            direccion=form.direccion.data
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('Cliente agregado con éxito!', 'success')
        return redirect(url_for('clientes'))

    return render_template('clientes.html', form=form, clientes=clientes, show_back_button=True)

@app.route('/clientes/editar/<int:id>', methods=['POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        cliente.nombre = request.form.get('nombre')
        cliente.email = request.form.get('email')
        cliente.telefono = request.form.get('telefono')
        cliente.documento_identidad = request.form.get('documento_identidad')
        cliente.direccion = request.form.get('direccion')
        db.session.commit()
        flash('Cliente actualizado con éxito!', 'success')
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash('Error al actualizar el cliente: ' + str(e), 'error')
    return redirect(url_for('clientes'))

@app.route('/clientes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado con éxito!', 'success')
    return redirect(url_for('clientes'))

@app.route('/get_cliente_details/<int:cliente_id>')
@login_required
def get_cliente_details(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    cliente_dict = {
        'id': cliente.id,
        'nombre': cliente.nombre,
        'email': cliente.email,
        'telefono': cliente.telefono,
        'direccion': cliente.direccion,
        'documento_identidad': cliente.documento_identidad
    }
    return jsonify(cliente_dict)

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    session['previous_page'] = url_for('dashboard')

    # Obtener el usuario actual
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Actualizar datos desde el formulario
        user.name = request.form.get('nombre', '')
        user.email = request.form.get('email', '')
        user.telefono = request.form.get('telefono', '')  # Actualizar el teléfono
        db.session.commit()
        flash('Perfil actualizado con éxito!', 'success')
        return redirect(url_for('perfil'))

    # Pasar los datos del usuario a la plantilla
    return render_template('perfil.html',
                          nombre=user.name,
                          email=user.email,
                          telefono=user.telefono,  # Pasar el teléfono desde el modelo
                          direccion="",  # Este campo no existe en el modelo actual
                          biografia="",
                          show_back_button=True)

@app.route('/ventas', methods=['GET', 'POST'])
@login_required
def ventas():
    session['previous_page'] = url_for('dashboard')
    form = NuevaVentaForm()
    if request.method == 'POST':
        # Aquí puedes manejar la lógica para crear una nueva venta
        cliente_id = request.form.get('cliente_id')
        producto_id = request.form.get('producto_id')
        total = request.form.get('total')
        
        nueva_venta = Venta(cliente_id=cliente_id, total=total, producto_id=producto_id)
        db.session.add(nueva_venta)
        db.session.commit()
        flash('Venta registrada exitosamente', 'success')
        
        return redirect(url_for('ventas'))

    # Si es un GET, mostrar la página de ventas
    ventas = Venta.query.all()  # Recuperar todas las ventas
    # Recuperar categorías y productos
    categorias = Categoria.query.all()  
    productos = Producto.query.all()  

    
    # Calcular estadísticas
    total_ingresos = sum(venta.total for venta in ventas)
    total_ventas = len(ventas)
    ventas_pendientes = sum(1 for venta in ventas if venta.estado == 'pendiente')

    # Calcular incremento (ajusta la lógica según tus necesidades)
    if total_ventas > 0:
        # Suponiendo que tienes una forma de obtener el total del mes anterior
        total_ventas_anterior = 20  # Cambia esto por la lógica real
        incremento = ((total_ventas - total_ventas_anterior) / total_ventas_anterior) * 100
    else:
        incremento = 0  # Si no hay ventas, el incremento es 0

    # Recuperar el cliente correspondiente (ajustar según la lógica de tu aplicación)
    cliente_id = request.args.get('cliente_id')  # Suponiendo que el cliente_id se pasa como parámetro en la URL
    cliente = Cliente.query.get(cliente_id) if cliente_id else None

    return render_template('ventas.html', ventas=ventas, total_ingresos=total_ingresos, total_ventas=total_ventas, ventas_pendientes=ventas_pendientes, incremento=incremento, form=form, productos=productos, cliente=cliente, show_back_button=True)

@app.route('/ventas/<int:venta_id>')
@login_required
def ver_detalle_venta(venta_id):
        venta = Venta.query.get_or_404(venta_id)
        return render_template('detalle_venta.html', venta=venta)

@app.route('/ventas/editar/<int:venta_id>', methods=['GET', 'POST'])
@login_required
def editar_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    if request.method == 'POST':
        # Actualizar la venta con los datos del formulario
        venta.cliente_id = request.form.get('cliente_id')
        venta.total = request.form.get('total')
        db.session.commit()
        flash('Venta actualizada exitosamente', 'success')
        return redirect(url_for('ventas'))
    return render_template('editar_venta.html', venta=venta)

@app.route('/ventas/eliminar/<int:venta_id>', methods=['POST'])
@login_required
def eliminar_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    db.session.delete(venta)
    db.session.commit()
    flash('Venta eliminada exitosamente', 'success')
    return redirect(url_for('ventas'))

@app.route('/productos')
@login_required
def productos():
    session['previous_page'] = url_for('dashboard')
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    subcategorias = Subcategoria.query.all()
    proveedores = Proveedor.query.all()

    # Manejo de errores: verificar si hay datos
    if not productos and not categorias and not subcategorias and not proveedores:
        return render_template('productos.html', message='No hay productos, categorías, subcategorías o proveedores disponibles.')

    form = ProductoForm()  # Create form instance for CSRF token
    return render_template('productos.html', 
                    productos=productos,
                    categorias=categorias,
                    subcategorias=subcategorias,
                    proveedores=proveedores,
                    form=form,
                    show_back_button=True)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        # Captura de datos
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        descripcion = request.form.get('descripcion')
        categoria_id = request.form.get('categoria_id')
        subcategoria_id = request.form.get('subcategoria_id')
        proveedor_id = request.form.get('proveedor_id')
        imagen = request.files.get('imagen')

        # Convert empty strings to None for integer fields
        if categoria_id == '':
            categoria_id = None
        if subcategoria_id == '':
            subcategoria_id = None
        if proveedor_id == '':
            proveedor_id = None
        if stock == '':
            stock = 0
            
        # Validaciones
        if not codigo or not nombre:
            flash('El código y el nombre son obligatorios', 'error')
            return redirect(url_for('productos'))

        # Guardar en la base de datos
        nuevo_producto = Producto(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            stock=stock,
            descripcion=descripcion,
            categoria_id=categoria_id,
            subcategoria_id=subcategoria_id,
            proveedor_id=proveedor_id,
            imagen=imagen.filename if imagen else None
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('productos'))

    # GET request - mostrar formulario
    return render_template('productos.html', show_back_button=True)

@app.route('/productos/editar/<int:id>', methods=['POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])
        producto.codigo = request.form['codigo']
        producto.categoria_id = request.form['categoria_id'] if request.form['categoria_id'] != '' else None

        if 'subcategoria_id' in request.form:
            producto.subcategoria_id = request.form['subcategoria_id'] if request.form['subcategoria_id'] != '' else None
        if 'proveedor_id' in request.form:
            producto.proveedor_id = request.form['proveedor_id'] if request.form['proveedor_id'] != '' else None
        
        # Manejo de la imagen
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                producto.imagen = f'uploads/{filename}'

        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        
    return redirect(url_for('productos'))

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
        
    return redirect(url_for('productos'))

@app.route('/get_producto_details/<int:id>')
@login_required
def get_producto_details(id):
    producto = Producto.query.get_or_404(id)
    producto_dict = {
        'id': producto.id,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'precio': producto.precio,
        'stock': producto.stock,
        'codigo': producto.codigo,
        'imagen': producto.imagen,
        'categoria_id': producto.categoria_id,
        'categoria_nombre': producto.categoria_parent.nombre if producto.categoria_parent else None,
        'subcategoria_id': producto.subcategoria_id,
        'subcategoria_nombre': producto.subcategoria_parent.nombre if producto.subcategoria_parent else None,
        'proveedor_id': producto.proveedor_id,
        'proveedor_nombre': producto.proveedor.nombre if producto.proveedor else None
    }
    return jsonify(producto_dict)

@app.route('/proveedores', methods=['GET', 'POST'])
@login_required
def proveedores():
    if request.method == 'POST':
        nombre = request.form.get('provider_name')
        contacto = request.form.get('provider_contact')
        email = request.form.get('provider_email')
        telefono = request.form.get('provider_phone')
        direccion = request.form.get('provider_address')
        descripcion = request.form.get('provider_description')

        # Mensaje de depuración
        print(f'Intentando agregar proveedor: {nombre}, {contacto}, {email}, {telefono}, {direccion}, {descripcion}')

        # Verifica que el nombre no sea None o vacío
        if not nombre:
            flash('El nombre es obligatorio.', 'error')
            return redirect(url_for('proveedores'))

        nuevo_proveedor = Proveedor(
            nombre=nombre,
            contacto=contacto,
            email=email,
            telefono=telefono,
            direccion=direccion,
            descripcion=descripcion
        )
        try:
            db.session.add(nuevo_proveedor)
            db.session.commit()
            flash('Proveedor agregado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash(f'Error al agregar proveedor: {str(e)}', 'error')
        
        return redirect(url_for('proveedores'))

    proveedores = Proveedor.query.all()  # Obtener todos los proveedores
    return render_template('proveedores.html', proveedores=proveedores, show_back_button=True)

@app.route('/proveedores/editar/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(proveedor_id):
    proveedor = Proveedor.query.get(proveedor_id)
    if request.method == 'POST':
        # Lógica para actualizar el proveedor
        proveedor.nombre = request.form.get('provider_name')
        proveedor.contacto = request.form.get('provider_contact')
        proveedor.email = request.form.get('provider_email')
        proveedor.telefono = request.form.get('provider_phone')
        proveedor.direccion = request.form.get('provider_address')
        proveedor.descripcion = request.form.get('provider_description')

        try:
            db.session.commit()
            flash('Proveedor actualizado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'error')
        proveedor.nombre = request.form.get('provider_name')
        proveedor.contacto = request.form.get('provider_contact')
        proveedor.email = request.form.get('provider_email')
        proveedor.telefono = request.form.get('provider_phone')
        proveedor.direccion = request.form.get('provider_address')
        db.session.commit()
        proveedor.descripcion = request.form.get('provider_description')
        try:
            db.session.commit()
            flash('Proveedor actualizado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'error')
        return redirect(url_for('proveedores'))

    return render_template('editar_proveedor.html', proveedor=proveedor, show_back_button=True)

@app.route('/get_proveedor_details/<int:proveedor_id>')
@login_required
def get_proveedor_details(proveedor_id):
    proveedor = Proveedor.query.get(proveedor_id)
    if proveedor:
        return jsonify({
            'nombre': proveedor.nombre,
               'contacto': proveedor.contacto,
               'email': proveedor.email,
               'telefono': proveedor.telefono,
               'direccion': proveedor.direccion,
               'descripcion': proveedor.descripcion
           })
    else:
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    
@app.route('/proveedores/eliminar/<int:proveedor_id>', methods=['POST'])
@login_required
def eliminar_proveedor(proveedor_id):
    proveedor = Proveedor.query.get(proveedor_id)
    if proveedor:
       db.session.delete(proveedor)
       db.session.commit()
       flash('Proveedor eliminado exitosamente.', 'success')
    else:
       flash('Proveedor no encontrado.', 'error')
    return redirect(url_for('proveedores'))

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html', show_back_button=False)  # No mostramos boton de regreso

@app.route('/get_previous_page')
def get_previous_page():
    # Devuelve la URL de la página anterior desde la sesión de Flask
    return jsonify({'previous_page': session.get('previous_page')})


if __name__ == '__main__':
     with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
        initialize_data()  # Inicializa los datos de ejemplo
        logging.debug('Conexión a la base de datos establecida correctamente.')
     app.run(debug=True)