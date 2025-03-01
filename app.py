import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Crear la aplicación Flask
app = Flask(__name__, template_folder='templates')
app.secret_key = 'tu_clave_secreta_123'  # Cambiado por una clave más segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/db_vcbikes'
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Inicializa Flask-Migrate

# Inicializar listas y contadores
CATEGORIAS = []
CATEGORY_ID_COUNTER = 1
EMPLEADOS = []
EMPLEADO_ID_COUNTER = 1
# Modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Guarda el hash de la contraseña
    name = db.Column(db.String(100), nullable=True) # Agregamos el nombre

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Decorator para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder.', 'error')
            return redirect(url_for('login'))
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

        user = User.query.filter_by(username=username).first() # Busca el usuario por nombre de usuario

        if user and user.check_password(password): # Verifica si el usuario existe y la contraseña es correcta
            session['user_id'] = user.id  # Guarda el ID del usuario en la sesión
            session['user_name'] = user.name # Guarda el nombre del usuario en la sesión
            flash('Has iniciado sesión exitosamente!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('nombre') # Obtiene el nombre del formulario
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

        # Crea un nuevo usuario
        new_user = User(username=username, email=email, name=name) # Usa el parametro nombre
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Te has registrado exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

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
    global CATEGORY_ID_COUNTER  # Necesario para modificar la variable global
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        category_description = request.form.get('category_description')

        # Validación básica (¡NECESITAS MÁS VALIDACIÓN EN PRODUCCIÓN!)
        if not category_name:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return redirect(url_for('categorias'))

        # Crear la nueva categoría (simulando un objeto de base de datos)
        new_category = {
            'id': CATEGORY_ID_COUNTER,
            'name': category_name,
            'description': category_description
        }
        CATEGORY_ID_COUNTER += 1
        CATEGORIES.append(new_category)
        flash('Categoría agregada con éxito!', 'success')
        return redirect(url_for('categorias'))

    return render_template('categorias.html', show_back_button=True) # Mostramos el boton de regreso


@app.route('/categorias/editar/<int:category_id>', methods=['GET', 'POST'])
@login_required
def editar_categoria(category_id):
    category = next((c for c in CATEGORIES if c['id'] == category_id), None)
    if not category:
        flash('Categoría no encontrada.', 'error')
        return redirect(url_for('categorias'))

    if request.method == 'POST':
        category_name = request.form.get('category_name')
        category_description = request.form.get('category_description')

        # Validación básica (¡NECESITAS MÁS VALIDACIÓN EN PRODUCCIÓN!)
        if not category_name:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return redirect(url_for('editar_categoria', category_id=category_id))

        # Actualizar la categoría
        category['name'] = category_name
        category['description'] = category_description
        flash('Categoría actualizada con éxito!', 'success')
        return redirect(url_for('categorias'))

    return render_template('editar_categoria.html', category=category, show_back_button=True)

@app.route('/categorias/eliminar/<int:category_id>', methods=['POST'])
@login_required
def eliminar_categoria(category_id):
    global CATEGORIES
    CATEGORIES = [c for c in CATEGORIES if c['id'] != category_id]
    flash('Categoría eliminada con éxito!', 'success')
    return redirect(url_for('categorias'))

@app.route('/subcategorias', methods=['GET', 'POST'])
@login_required
def subcategorias():
    return render_template('subcategorias.html', show_back_button=True) # Mostramos el boton de regreso


@app.route('/configuracion_usuario')
@login_required
def configuracion_usuario():
    return render_template('configuracion_usuario.html')

@app.route('/empleados', methods=['GET', 'POST'])
@login_required
def empleados():
    global EMPLEADO_ID_COUNTER
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cargo = request.form.get('cargo')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        fecha_contratacion = request.form.get('contratacion')
        # ... (obtener los demás campos del formulario) ...

        # Validación (¡MUY IMPORTANTE!)
        if not nombre or not cargo or not email:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('empleados'))

        nuevo_empleado = {
            'id': EMPLEADO_ID_COUNTER,
            'nombre': nombre,
            'cargo': cargo,
            'email': email,
            'telefono': telefono,
            'direccion': direccion,
            'fecha_contratacion': fecha_contratacion,
            # ... (asignar los demás campos) ...
        }
        EMPLEADOS.append(nuevo_empleado)
        EMPLEADO_ID_COUNTER += 1
        flash('Empleado agregado con éxito!', 'success')
        return redirect(url_for('empleados'))

    return render_template('empleados.html', empleados=EMPLEADOS, show_back_button=True) # Mostramos el boton de regreso



@app.route('/empleados/editar/<int:empleado_id>', methods=['GET', 'POST'])
@login_required
def editar_empleado(empleado_id):
    empleado = next((e for e in EMPLEADOS if e['id'] == empleado_id), None)
    if not empleado:
        flash('Empleado no encontrado.', 'error')
        return redirect(url_for('empleados'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cargo = request.form.get('cargo')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        fecha_contratacion = request.form.get('contratacion')
        # ... (obtener los demás campos del formulario) ...

        # Validación (¡MUY IMPORTANTE!)
        if not nombre or not cargo or not email:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('editar_empleado', empleado_id=empleado_id))

        empleado['nombre'] = nombre
        empleado['cargo'] = cargo
        empleado['email'] = email
        empleado['telefono'] = telefono
        empleado['direccion'] = direccion
        empleado['contratacion'] = fecha_contratacion
        # ... (actualizar los demás campos) ...
        flash('Empleado actualizado con éxito!', 'success')
        return redirect(url_for('empleados'))

    return render_template('editar_empleado.html', empleado=empleado, show_back_button=True)


@app.route('/empleados/eliminar/<int:empleado_id>', methods=['POST'])
@login_required
def eliminar_empleado(empleado_id):
    global EMPLEADOS
    EMPLEADOS = [e for e in EMPLEADOS if e['id'] != empleado_id]
    flash('Empleado eliminado con éxito!', 'success')
    return redirect(url_for('empleados'))

@app.route('/clientes')
@login_required
def clientes():
    return render_template('clientes.html', show_back_button=True) # Mostramos el boton de regreso


# Datos del usuario (simulación - ¡NO USAR EN PRODUCCIÓN!)
USUARIO_NOMBRE = "Víctor"
USUARIO_APELLIDO = "Cabas"
USUARIO_EMAIL = "victor@vcbikes.com"
USUARIO_TELEFONO = "+57 300 123 4567"
USUARIO_DIRECCION = "Calle 123 #45-67"
USUARIO_CIUDAD = "Bogotá"
USUARIO_ESTADO = "Cundinamarca"
USUARIO_CODIGO_POSTAL = "110111"
USUARIO_BIOGRAFIA = "Administrador del sistema de inventario VcBikes."

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    global USUARIO_NOMBRE, USUARIO_APELLIDO, USUARIO_EMAIL, USUARIO_TELEFONO, USUARIO_DIRECCION, USUARIO_CIUDAD, USUARIO_ESTADO, USUARIO_CODIGO_POSTAL, USUARIO_BIOGRAFIA

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        ciudad = request.form.get('ciudad')
        estado = request.form.get('estado')
        codigo_postal = request.form.get('codigo_postal')
        biografia = request.form.get('biografia')

        # Validar los datos (¡IMPORTANTE en una aplicación real!)
        if not nombre or not apellido or not email:
            flash('Nombre, apellido y correo electrónico son obligatorios.', 'error')
            return redirect(url_for('perfil'))

        # Actualizar los datos (simulación - ¡NO USAR EN PRODUCCIÓN!)
        USUARIO_NOMBRE = nombre
        USUARIO_APELLIDO = apellido
        USUARIO_EMAIL = email
        USUARIO_TELEFONO = telefono
        USUARIO_DIRECCION = direccion
        USUARIO_CIUDAD = ciudad
        USUARIO_ESTADO = estado
        USUARIO_CODIGO_POSTAL = codigo_postal
        USUARIO_BIOGRAFIA = biografia

        flash('Perfil actualizado con éxito!', 'success')
        return redirect(url_for('perfil'))

    # Pasar los datos a la plantilla
    return render_template('perfil.html',
                           nombre=USUARIO_NOMBRE,
                           apellido=USUARIO_APELLIDO,
                           email=USUARIO_EMAIL,
                           telefono=USUARIO_TELEFONO,
                           direccion=USUARIO_DIRECCION,
                           ciudad=USUARIO_CIUDAD,
                           estado=USUARIO_ESTADO,
                           codigo_postal=USUARIO_CODIGO_POSTAL,
                           biografia=USUARIO_BIOGRAFIA, show_back_button=True)

@app.route('/ventas')
@login_required
def ventas():
    return render_template('ventas.html', show_back_button=True)

@app.route('/productos')
@login_required
def productos():
    return render_template('productos.html', show_back_button=True)

@app.route('/proveedores', methods=['GET', 'POST'])
@login_required
def proveedores():
    return render_template('proveedores.html', show_back_button=True)

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html', show_back_button=False) # No mostramos boton de regreso

@app.route('/get_previous_page')
def get_previous_page():
    # Devuelve la URL de la página anterior desde la sesión de Flask
    return jsonify({'previous_page': session.get('previous_page')})


if __name__ == '__main__':
     with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
     app.run(debug=True)