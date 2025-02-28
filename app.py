import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Crear la aplicación Flask
app = Flask(__name__, template_folder='templates')
app.secret_key = 'tu_clave_secreta_123'  # Cambiado por una clave más segura

# Usuario de prueba (en producción usar base de datos)
USERS = {
    "admin": {
        "password": "admin123",
        "name": "Administrador"
    }
}

# Simulación de base de datos en memoria (¡NO PARA PRODUCCIÓN!)
CATEGORIES = []
CATEGORY_ID_COUNTER = 1  # Para simular IDs autoincrementales

EMPLEADOS = []
EMPLEADO_ID_COUNTER = 1

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
    return render_template('index.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')
        flash('Mensaje enviado con éxito. Nos pondremos en contacto contigo pronto.')
        return redirect(url_for('contacto'))
    return render_template('contacto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username]["password"] == password:
            session['user_id'] = username
            session['user_name'] = USERS[username]["name"]
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
    return render_template('registro.html')

@app.route('/recuperar-password', methods=['GET', 'POST'])
def recuperar_password():
    return render_template('recuperacion.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

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

    return render_template('categorias.html', categories=CATEGORIES)  # Pasar las categorías a la plantilla

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

    return render_template('editar_categoria.html', category=category)

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
    return render_template('subcategorias.html')

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

    return render_template('empleados.html', empleados=EMPLEADOS)


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

    return render_template('editar_empleado.html', empleado=empleado)


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
    return render_template('clientes.html')

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
                           biografia=USUARIO_BIOGRAFIA)

@app.route('/ventas')
@login_required
def ventas():
    return render_template('ventas.html')

@app.route('/productos')
@login_required
def productos():
    return render_template('productos.html')

@app.route('/proveedores', methods=['GET', 'POST'])
@login_required
def proveedores():
    return render_template('proveedores.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')


if __name__ == '__main__':
    app.run(debug=True)