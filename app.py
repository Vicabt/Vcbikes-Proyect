import os
import secrets
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from models import db, User, Empleado, Categoria, Cliente, Subcategoria, Producto, Proveedor, Venta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import logging
from forms import ProductoForm, NuevaVentaForm, ClienteForm

# Load environment variables from .env file
load_dotenv()

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
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html', show_back_button=False)


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
    try:
        # Estadísticas básicas - solo contar registros activos (estado=0)
        total_productos = Producto.query.filter_by(estado=0).count()
        total_clientes = Cliente.query.filter_by(estado=0).count()
        
        # Estadísticas de ventas
        hoy = datetime.now()
        primer_dia_mes = datetime(hoy.year, hoy.month, 1)
        
        # Ventas del mes - solo ventas activas
        ventas_mes = Venta.query.filter(Venta.fecha >= primer_dia_mes, Venta.estado_registro==0).count()
        
        # Ingresos del mes actual - solo ventas activas
        ingresos_mes = db.session.query(db.func.sum(Venta.total))\
            .filter(Venta.fecha >= primer_dia_mes, Venta.estado_registro==0)\
            .scalar() or 0
        ingresos_mes = round(float(ingresos_mes), 2)
        
        # Total histórico de ingresos - solo ventas activas
        total_ingresos = db.session.query(db.func.sum(Venta.total)).filter(Venta.estado_registro==0).scalar() or 0
        total_ingresos = round(float(total_ingresos), 2)
        
        # Productos con stock bajo (menos de 5 unidades) - solo productos activos
        umbral_stock_bajo = 5
        productos_bajo_stock = Producto.query.filter(Producto.stock <= umbral_stock_bajo, Producto.estado==0).count()
        
        # Productos más vendidos (top 5) - solo productos y ventas activos
        productos_mas_vendidos = db.session.query(
            Producto.nombre,
            db.func.count(Venta.id).label('total_ventas')
        ).join(Venta)\
         .filter(Producto.estado==0, Venta.estado_registro==0)\
         .group_by(Producto.id)\
         .order_by(db.text('total_ventas DESC'))\
         .limit(5)\
         .all()
        
        # Categorías más populares - solo categorías y productos activos
        categorias_populares = db.session.query(
            Categoria.nombre,
            db.func.count(Producto.id).label('total_productos')
        ).join(Producto)\
         .filter(Categoria.estado==0, Producto.estado==0)\
         .group_by(Categoria.id)\
         .order_by(db.text('total_productos DESC'))\
         .limit(5)\
         .all()
        
        # Total de proveedores - solo proveedores activos
        total_proveedores = Proveedor.query.filter_by(estado=0).count()
        
        # Total de empleados - solo empleados activos
        total_empleados = Empleado.query.filter_by(estado=0).count()
        
        # Promedio de venta por cliente - solo ventas activas
        promedio_venta = db.session.query(
            db.func.avg(Venta.total)
        ).filter(Venta.estado_registro==0).scalar() or 0
        promedio_venta = round(float(promedio_venta), 2)
        
        return render_template('dashboard.html',
                             total_productos=total_productos,
                             ventas_mes=ventas_mes,
                             total_clientes=total_clientes,
                             productos_bajo_stock=productos_bajo_stock,
                             total_ingresos=total_ingresos,
                             ingresos_mes=ingresos_mes,
                             productos_mas_vendidos=productos_mas_vendidos,
                             categorias_populares=categorias_populares,
                             total_proveedores=total_proveedores,
                             total_empleados=total_empleados,
                             promedio_venta=promedio_venta,
                             show_back_button=False)
                             
    except Exception as e:
        app.logger.error(f'Error en el dashboard: {str(e)}')
        flash('Error al cargar los datos del dashboard', 'error')
        return render_template('dashboard.html', 
                             total_productos=0,
                             ventas_mes=0,
                             total_clientes=0,
                             productos_bajo_stock=0,
                             total_ingresos=0,
                             ingresos_mes=0,
                             productos_mas_vendidos=[],
                             categorias_populares=[],
                             total_proveedores=0,
                             total_empleados=0,
                             promedio_venta=0,
                             show_back_button=False)


@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    session['previous_page'] = url_for('dashboard')
    # Solo mostrar categorías activas (estado=0)
    categorias = Categoria.query.filter_by(estado=0).all()
    return render_template('categorias.html', categories=categorias, show_back_button=True)

@app.route('/categorias/editar', methods=['POST'])
@login_required
def editar_categoria():
    if not request.is_json:
        return jsonify({'error': 'La solicitud debe ser JSON'}), 400

    data = request.get_json()
    category_id = data.get('category_id')
    category_name = data.get('category_name')
    category_description = data.get('category_description')

    if not category_id:
        return jsonify({'error': 'ID de categoría no válido'}), 400

    categoria = Categoria.query.get_or_404(category_id)

    if not category_name:
        return jsonify({'error': 'El nombre de la categoría es obligatorio'}), 400

    try:
        categoria.nombre = category_name
        categoria.descripcion = category_description
        db.session.commit()
        return jsonify({'message': 'Categoría actualizada con éxito'}), 200  # Devuelve JSON
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar la categoría: {str(e)}'}), 500

@app.route('/categorias/eliminar/<int:category_id>', methods=['POST'])
@login_required
def eliminar_categoria(category_id):
    categoria = Categoria.query.get_or_404(category_id)
    try:
        # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
        categoria.estado = 1
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
    # Solo mostrar categorías y subcategorías activas (estado=0)
    categorias = Categoria.query.filter_by(estado=0).all()
    subcategorias = Subcategoria.query.filter_by(estado=0).all()
    return render_template('subcategorias.html', categorias=categorias, subcategorias=subcategorias, show_back_button=True)

@app.route('/get_subcategorias/<int:categoria_id>')
@login_required
def get_subcategorias(categoria_id):
    # Solo mostrar subcategorías activas (estado=0)
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id, estado=0).all()
    subcategorias_dict = [{'id': sub.id, 'nombre': sub.nombre} for sub in subcategorias]
    return jsonify(subcategorias_dict)

@app.route('/actualizar_subcategoria/<int:subcategory_id>', methods=['POST'])
@login_required
def actualizar_subcategoria(subcategory_id):
    # Obtener datos del formulario
    parent_category_id = request.form.get('parent_category')
    subcategory_name = request.form.get('subcategory_name')
    subcategory_description = request.form.get('subcategory_description')
    
    # Buscar la subcategoría por ID
    subcategoria = Subcategoria.query.get_or_404(subcategory_id)
    
    # Actualizar los datos
    subcategoria.categoria_id = parent_category_id
    subcategoria.nombre = subcategory_name
    subcategoria.descripcion = subcategory_description
    
    try:
        # Guardar los cambios
        db.session.commit()
        flash('Subcategoría actualizada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la subcategoría: {str(e)}', 'error')
    
    return redirect(url_for('subcategorias'))

@app.route('/eliminar_subcategoria/<int:subcategory_id>', methods=['POST'])
@login_required
def eliminar_subcategoria(subcategory_id):
    subcategoria = Subcategoria.query.get_or_404(subcategory_id)
    try:
        # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
        subcategoria.estado = 1
        db.session.commit()
        flash('Subcategoría eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la subcategoría: {str(e)}', 'error')
    
    return redirect(url_for('subcategorias'))

@app.route('/configuracion_usuario')
@login_required
def configuracion_usuario():
    return render_template('configuracion_usuario.html')

from datetime import datetime

@app.route('/empleados', methods=['GET', 'POST'])
@login_required
def empleados():
    session['previous_page'] = url_for('dashboard')
    # Solo mostrar empleados activos (estado=0)
    empleados = Empleado.query.filter_by(estado=0).all()
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
        # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
        empleado.estado = 1
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
    session['previous_page'] = url_for('dashboard')
    # Crear una instancia del formulario para CSRF token
    form = ClienteForm()
    
    if form.validate_on_submit():  # Si el formulario se envía y es válido
        if Cliente.query.filter_by(email=form.email.data).first():
            flash('El email ya está registrado.', 'error')
            return redirect(url_for('clientes'))

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
    
    # Solo mostrar clientes activos (estado=0)
    clientes = Cliente.query.filter_by(estado=0).all()
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
    # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
    cliente.estado = 1
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
    
    # Obtener todos los clientes activos para el selector
    clientes = Cliente.query.filter_by(estado=0).all()
    
    if request.method == 'POST':
        try:
            cliente_id = request.form.get('cliente_id')
            producto_id = request.form.get('producto_id')
            total = request.form.get('total')
            estado = request.form.get('estado', 'pendiente')  # Por defecto es pendiente
            
            # Crear nueva venta
            nueva_venta = Venta(
                cliente_id=cliente_id,
                producto_id=producto_id,
                total=total,
                estado=estado,
                fecha=datetime.now()
            )
            
            # Si la venta está completada, actualizar el stock del producto
            if estado == 'completado':
                producto = Producto.query.get(producto_id)
                if producto and producto.stock > 0:
                    producto.stock -= 1
                else:
                    raise ValueError('No hay stock disponible para este producto')
            
            db.session.add(nueva_venta)
            db.session.commit()
            flash('Venta registrada exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la venta: {str(e)}', 'error')
        
        return redirect(url_for('ventas'))

    # Si es un GET, mostrar la página de ventas
    # Solo mostrar ventas activas (estado_registro=0)
    ventas = Venta.query.filter_by(estado_registro=0).all()
    # Recuperar categorías y productos activos
    categorias = Categoria.query.filter_by(estado=0).all()
    productos = Producto.query.filter_by(estado=0).all()

    # Calcular estadísticas
    total_ingresos = sum(venta.total for venta in ventas)
    total_ventas = len(ventas)
    ventas_pendientes = sum(1 for venta in ventas if venta.estado == 'pendiente')

    # Calcular incremento comparando mes actual vs mes anterior
    # Obtener el primer día del mes actual y del mes anterior
    hoy = datetime.now()
    primer_dia_mes_actual = datetime(hoy.year, hoy.month, 1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    primer_dia_mes_anterior = datetime(ultimo_dia_mes_anterior.year, ultimo_dia_mes_anterior.month, 1)

    # Contar ventas del mes actual y del mes anterior
    ventas_mes_actual = sum(1 for venta in ventas if primer_dia_mes_actual <= venta.fecha <= hoy)
    ventas_mes_anterior = sum(1 for venta in ventas if primer_dia_mes_anterior <= venta.fecha < primer_dia_mes_actual)

    # Calcular incremento
    if ventas_mes_anterior > 0:
        incremento = ((ventas_mes_actual - ventas_mes_anterior) / ventas_mes_anterior) * 100
    else:
        incremento = 100 if ventas_mes_actual > 0 else 0

    return render_template('ventas.html', 
                         ventas=ventas, 
                         total_ingresos=total_ingresos, 
                         total_ventas=total_ventas, 
                         ventas_pendientes=ventas_pendientes, 
                         incremento=incremento, 
                         form=form, 
                         productos=productos, 
                         clientes=clientes,  # Agregamos la lista de clientes
                         show_back_button=True)

@app.route('/ventas/editar/<int:venta_id>', methods=['POST'])
@login_required
def editar_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    if request.method == 'POST':
        try:
            nuevo_estado = request.form.get('estado')
            estado_anterior = venta.estado
            
            # Actualizar la venta con los datos del formulario
            venta.cliente_id = request.form.get('cliente_id')
            venta.producto_id = request.form.get('producto_id')
            venta.total = request.form.get('total')
            venta.estado = nuevo_estado
            
            # Manejar el stock según el cambio de estado
            producto = Producto.query.get(venta.producto_id)
            if producto:
                # Si la venta pasa a completada
                if nuevo_estado == 'completado' and estado_anterior != 'completado':
                    if producto.stock > 0:
                        producto.stock -= 1
                    else:
                        raise ValueError('No hay stock disponible para este producto')
                # Si la venta deja de estar completada
                elif estado_anterior == 'completado' and nuevo_estado != 'completado':
                    producto.stock += 1
            
            db.session.commit()
            flash('Venta actualizada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la venta: {str(e)}', 'error')
        
        return redirect(url_for('ventas'))
    
    return redirect(url_for('ventas'))

@app.route('/ventas/eliminar/<int:venta_id>', methods=['POST'])
@login_required
def eliminar_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    try:
        # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
        venta.estado_registro = 1
        db.session.commit()
        flash('Venta eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas'))

@app.route('/productos')
@login_required
def productos():
    session['previous_page'] = url_for('dashboard')
    # Crear una instancia del formulario para CSRF token
    form = ProductoForm()
    # Solo mostrar productos, categorías y subcategorías activos (estado=0)
    productos = Producto.query.filter_by(estado=0).all()
    categorias = Categoria.query.filter_by(estado=0).all()
    subcategorias = Subcategoria.query.filter_by(estado=0).all()
    proveedores = Proveedor.query.filter_by(estado=0).all()
    return render_template('productos.html', form=form, productos=productos, categorias=categorias, subcategorias=subcategorias, proveedores=proveedores, show_back_button=True)

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

        # Procesar la imagen si se ha subido una
        imagen_path = None
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            # Guardar el archivo en la carpeta de uploads
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Guardar la ruta relativa a la carpeta static
            imagen_path = f'uploads/{filename}'

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
            imagen=imagen_path  # Guardar la ruta relativa
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
        # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
        producto.estado = 1
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
    session['previous_page'] = url_for('dashboard')
    # Solo mostrar proveedores activos (estado=0)
    proveedores = Proveedor.query.filter_by(estado=0).all()
    return render_template('proveedores.html', proveedores=proveedores, show_back_button=True)

@app.route('/proveedores/editar/<int:proveedor_id>', methods=['POST'])
@login_required
def editar_proveedor(proveedor_id):
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos del proveedor
            proveedor.nombre = request.form.get('provider_name')
            proveedor.contacto = request.form.get('provider_contact')
            proveedor.email = request.form.get('provider_email')
            proveedor.telefono = request.form.get('provider_phone')
            proveedor.direccion = request.form.get('provider_address')
            proveedor.descripcion = request.form.get('provider_description')
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'error')
        
        return redirect(url_for('proveedores'))
    
    return redirect(url_for('proveedores'))

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
       # En lugar de eliminar, cambiamos el estado a 1 (eliminado)
       proveedor.estado = 1
       db.session.commit()
       flash('Proveedor eliminado exitosamente.', 'success')
    else:
       flash('Proveedor no encontrado.', 'error')
    return redirect(url_for('proveedores'))

@app.route('/nosotros')
@login_required
def nosotros():
    return render_template('nosotros.html', show_back_button=False)  # No mostramos boton de regreso

@app.route('/get_previous_page')
def get_previous_page():
    # Devuelve la URL de la página anterior desde la sesión de Flask
    return jsonify({'previous_page': session.get('previous_page')})

@app.route('/cambiar_password', methods=['POST'])
@login_required
def cambiar_password():
    try:
        # Obtener datos del formulario
        password_actual = request.form.get('password_actual')
        password_nuevo = request.form.get('password_nuevo')
        password_confirmar = request.form.get('password_confirmar')

        # Obtener el usuario actual
        user = User.query.get(session['user_id'])

        # Verificar que la contraseña actual sea correcta
        if not user.check_password(password_actual):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('perfil'))

        # Verificar que las contraseñas nuevas coincidan
        if password_nuevo != password_confirmar:
            flash('Las contraseñas nuevas no coinciden', 'error')
            return redirect(url_for('perfil'))

        # Verificar que la contraseña nueva tenga al menos 8 caracteres
        if len(password_nuevo) < 8:
            flash('La contraseña nueva debe tener al menos 8 caracteres', 'error')
            return redirect(url_for('perfil'))

        # Actualizar la contraseña
        user.set_password(password_nuevo)
        db.session.commit()

        flash('Contraseña actualizada exitosamente', 'success')
        return redirect(url_for('perfil'))

    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar la contraseña', 'error')
        logging.error(f'Error al cambiar contraseña: {str(e)}')
        return redirect(url_for('perfil'))

@app.route('/get_proveedores')
@login_required
def get_proveedores():
    # Solo mostrar proveedores activos (estado=0)
    proveedores = Proveedor.query.filter_by(estado=0).all()
    proveedores_list = [{'id': p.id, 'nombre': p.nombre} for p in proveedores]
    return jsonify(proveedores_list)

if __name__ == '__main__':
     with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
        initialize_data()  # Inicializa los datos de ejemplo
        logging.debug('Conexión a la base de datos establecida correctamente.')
     app.run(debug=True)