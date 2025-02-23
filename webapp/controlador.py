
##### Librerias y Dependencias
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from functools import wraps
from datetime import datetime, timedelta
from webapp import app
import geocoder # Librería para obtener la geolocalización
import os

password = "ElGuada90.#"
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Middleware para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para validar si el usuario tiene un rol específico
def role_required(*required_roles):  # Acepta múltiples roles como argumentos
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'error')
                return redirect(url_for('login'))
            if session.get('role') not in required_roles:
                flash('No tienes permiso para acceder a esta página.', 'error')
                return redirect(url_for('login'))  # Redirigir a una página sin restricciones
            return f(*args, **kwargs)
        return decorated_function
    return decorator



##################### CONTROLADOR DE INDEX
@app.route('/')
@app.route('/home')
def home():
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "login.html",
        title = "EG90  Login",
        message = "Inicio de Sesion ",
        content =  formatted_now)  

    
# Configuración de la base de datos MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'administracion'
app.config['MYSQL_HOST'] = 'localhost'
mysql = MySQL(app)

# ADMINISTRATIVO
#########################################################################################
# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    if request.method == 'POST':
        usuario = request.form['Usuario']
        contraseña = request.form['Contraseña']
        
         # Conectar y usar DictCursor
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Usuarios WHERE Usuario = %s", (usuario,))
        user = cursor.fetchone()
        cursor.close() 
        
        if user:
            # Verificar contraseña del usuario
            stored_password_hash = user['Contraseña']

            if check_password_hash(stored_password_hash, contraseña):
                    # Guardar datos en la sesión
                    session['user_id'] = user['ID_Usuario']
                    session['username'] = user['Usuario']
                    session['role'] = user['Rol']
                    session.permanent = True  # Activar sesión persistente
                    app.permanent_session_lifetime = timedelta(days=7)  # Duración de la sesión
                    
                     # Registrar la acción de login
                    user_id = session.get('user_id')
                    user_name = session.get('username')
                    accion = f"Inicio de sesión exitoso: {user_name}"
                    
                    flash('Inicio de sesión exitoso', 'success') 
                    return redirect(url_for('historialmarcaciones'))
                    
            else:
                flash('Contraseña incorrecta', 'error')
        else:
            flash('Usuario no registrado', 'error')
    
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "login.html", 
        title="EG90 Login", 
        message="Marcaciones", 
        content=formatted_now)


# Ruta para registrar marcación
@app.route('/registromarcacion')
@login_required
def registromarcacion():
    user_id = session.get('user_id')
    user_name = session.get('username')

    if request.method == 'POST':
        if 'foto' not in request.files:
            flash('Debes seleccionar una foto.', 'error')
            return redirect(request.url)

        foto = request.files['foto']
        if foto.filename == '':
            flash('Ninguna foto seleccionada.', 'error')
            return redirect(request.url)

        # Securely save the image
        filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"  # Unique filename
        filepath = os.path.join(app.static_folder, 'imagenes', filename)  # Correct path
        foto.save(filepath)

        # Get geolocation (you might want to improve this)
        try:
            g = geocoder.ip('me') # Or use a more specific method if you have it.
            ubicacion = g.latlng  # Returns a tuple (latitude, longitude)
            ubicacion_str = f"{ubicacion[0]},{ubicacion[1]}" if ubicacion else "Ubicación no disponible"
        except Exception as e:
            ubicacion_str = "Error obteniendo ubicación"
            print(f"Geolocation error: {e}")  # Print for debugging

        fechahora = datetime.now()

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO Marcaciones (ID_Usuario, FechaHora, Ubicacion, Foto) VALUES (%s, %s, %s, %s)",
                           (user_id, fechahora, ubicacion_str, filename)) # Store filename, not path
            mysql.connection.commit()
            cursor.close()
            flash('Marcación registrada exitosamente.', 'success')
            return redirect(url_for('historialmarcaciones'))  # Redirect to history after success
        except Exception as e:
            mysql.connection.rollback()  # Important: Rollback on error
            flash(f'Error al registrar la marcación: {e}', 'error')
            print(f"Database error: {e}")  # Print for debugging
            return redirect(request.url)

    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "registromarcacion.html", 
        title="EG90 WebApp", 
        message="Marcacion ", 
        content=formatted_now)

    
# Ruta para mostrar el historial de las marcaciones    
@app.route('/historialmarcaciones')
@login_required
@role_required('Admin', 'SuperUser')
def historialmarcaciones():
    
    try:
        conn = mysql.connection
        cursor = conn.cursor(DictCursor) # Use DictCursor for easier access to data
        cursor.execute("""SELECT m.ID_Usuario, 
                          m.FechaHora, 
                          CONCAT(u.Nombre, ' ', u.Apellido) AS Nombre, 
                          m.Ubicacion, 
                          m.Foto 
                          FROM Marcaciones m 
                          JOIN Usuarios u ON m.ID_Usuario = u.ID_Usuario 
                          ORDER BY m.FechaHora DESC;""")
        marcaciones = cursor.fetchall()
        cursor.close()
    except Exception as e:
        flash(f"Error al cargar el historial: {e}", "error")
        print(f"Error fetching marcaciones: {e}") # Debugging
        marcaciones = [] # Return empty list in case of error

    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "historialmarcaciones.html", 
        title="EG90 WebApp", 
        message="Marcacion ", 
        content=formatted_now, 
        marcaciones=marcaciones)
    
    
# Ruta para mostrar loa usuarios actualizados    
@app.route('/usuarios')
@login_required
@role_required('Admin', 'SuperUser')
def usuarios():
    
    try:
        conn = mysql.connection
        cursor = conn.cursor(DictCursor) # Use DictCursor for easier access to data
        cursor.execute("SELECT * FROM Usuarios ORDER BY Fecha DESC")
        usuarios = cursor.fetchall()
        cursor.close()
    except Exception as e:
        flash(f"Error al cargar el usuarios: {e}", "error")
        print(f"Error fetching usuarios: {e}") # Debugging
        usuarios = [] # Return empty list in case of error

    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "usuarios.html", 
        title="EG90 WebApp", 
        message="Marcacion ", 
        content=formatted_now, 
        usuarios=usuarios)
    
# Controlador de Formulario para agregar nuevos usuarios               
##################################################################################
@app.route('/agregar_usuario', methods=['POST'])
@login_required  
@role_required('Admin', 'SuperUser')
def agregar_usuario():
    try:
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rol = request.form['rol']
        foto = request.files.get('foto')

        # Hash de la contraseña
        hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')  # Prueba con este método

        filename = None
        if foto:
            # Validación del archivo (tipo, tamaño, etc.)
            if foto.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                return jsonify({'success': False, 'message': 'Tipo de archivo no permitido'}), 400

            filename = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"  # o la extensión original
            filepath = os.path.join(app.static_folder, 'imagenes', filename)

            try:
                foto.save(filepath)
            except Exception as e:
                print(f"Error guardando la foto: {e}")
                return jsonify({'success': False, 'message': 'Error al guardar la foto'}), 500  # Internal Server Error

        # Usando un bloque 'with' para asegurar el cierre del cursor
        with mysql.connection.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO Usuarios (Usuario, Contraseña, Nombre, Apellido, Rol, Foto) VALUES (%s, %s, %s, %s, %s, %s)",
                               (usuario, hashed_password, nombre, apellido, rol, filename))
                mysql.connection.commit()
            except mysql.connector.Error as err:
                mysql.connection.rollback()
                print(f"Error en la base de datos: {err}")
                # Puedes redirigir a una página de error o mostrar un mensaje en la misma página
                return render_template("usuarios.html", error_message=f"Error en la base de datos: {err}"), 500

        return redirect(url_for('mostrar_usuarios'))  # Redirige a la función que renderiza usuarios.html

    except Exception as e:
        mysql.connection.rollback()
        print(f"Error general al agregar usuario: {e}")
        # Puedes redirigir a una página de error o mostrar un mensaje en la misma página
        return render_template(
            "usuarios.html", 
            error_message="Error al agregar usuario"
            ), 500
        

# Controlador de Formulario para editar usuarios               
##################################################################################        
@app.route('/editar_usuario/<int:user_id>', methods=['POST'])  # Incluye el ID del usuario en la URL
@login_required
@role_required('Admin', 'SuperUser')
def editar_usuario(user_id):  # Recibe el ID del usuario como argumento
    try:
        usuario = request.form['usuario']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rol = request.form['rol']
        foto = request.files.get('foto')
        contrasena = request.form.get('contrasena')  # Obtén la contraseña, pero no la requieras

        # Busca el usuario a editar
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Usuarios WHERE ID_Usuario = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                return render_template("usuarios.html", error_message="Usuario no encontrado"), 404

            # Hash de la contraseña (solo si se proporciona una nueva)
            if contrasena:
                hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')
            else:
                hashed_password = user[3] # Mantén la contraseña anterior si no se proporciona una nueva

            filename = user[6] # Usa la foto existente por defecto
            if foto:
                # Validación del archivo (tipo, tamaño, etc.)
                if foto.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                    return render_template("usuarios.html", error_message='Tipo de archivo no permitido'), 400

                filename = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                filepath = os.path.join(app.static_folder, 'imagenes', filename)

                try:
                    foto.save(filepath)
                except Exception as e:
                    print(f"Error guardando la foto: {e}")
                    return render_template("usuarios.html", error_message='Error al guardar la foto'), 500

            # Actualiza los datos del usuario
            try:
                cursor.execute("""
                    UPDATE Usuarios SET 
                        Usuario = %s, 
                        Contraseña = %s, 
                        Nombre = %s, 
                        Apellido = %s, 
                        Rol = %s, 
                        Foto = %s,
                        UsuarioModificacion = %s,
                        FechaModificacion = NOW()
                    WHERE ID_Usuario = %s
                """, (usuario, hashed_password, nombre, apellido, rol, filename, usuario, user_id))
                mysql.connection.commit()
            except mysql.connection.Error as err:
                mysql.connection.rollback()
                print(f"Error en la base de datos: {err}")
                return render_template("usuarios.html", error_message=f"Error en la base de datos: {err}"), 500

        return redirect(url_for('usuarios'))

    except Exception as e:
        mysql.connection.rollback()
        print(f"Error general al editar usuario: {e}")
        usuarios = [] # Return empty list in case of error
        return render_template(
            "usuarios.html", 
            usuarios=usuarios,
            error_message="Error al editar usuario"), 500        
    
    
 # Controlador para Registro de Marcacion               
##################################################################################   
@app.route('/registromarcacion', methods=['POST'])
@login_required
def registrar_marcacion():
    try:
        if 'user_id' not in session:
            flash("Debes iniciar sesión para registrar una marcación.", "error")
            return redirect(url_for('login'))  # Redirige al login si no hay sesión

        id_usuario = session['user_id']
        foto = request.files.get('foto')

        if not foto:
            flash("Debes seleccionar una foto.", "error")
            return redirect(request.referrer)  # Redirige a la misma página

        # Guardar la foto
        filename = f"{id_usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(app.static_folder, 'imagenes', filename)
        foto.save(filepath)

        # Obtener latitud y longitud desde la solicitud (enviadas por JavaScript)
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')

        if not latitud or not longitud:
            flash("No se pudo obtener la ubicación.", "error")
            ubicacion = "Ubicación no disponible"  # O un valor por defecto
        else:
            # Usar geocoding inverso con geocoder
            location = geocoder.reverse((latitud, longitud), provider='osm') # Puedes usar otro método
            ubicacion = location.address if location else "Ubicación no disponible"

        with mysql.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Marcaciones (ID_Usuario, Ubicacion, Foto) 
                VALUES (%s, %s, %s)
            """, (id_usuario, ubicacion, filename))
            mysql.connection.commit()
            
        with mysql.connection.cursor(DictCursor) as cursor:
            cursor.execute("SELECT Nombre, Apellido FROM Usuarios WHERE ID_Usuario = %s", (session['user_id'],))
            user_data = cursor.fetchone()

        if user_data:
            nombre_completo = f"{user_data['Nombre']} {user_data['Apellido']}"
        else:
            nombre_completo = "Usuario desconocido"  # Maneja el caso en que no se encuentra el usuario    

        flash(("Marcación registrada correctamente", nombre_completo), "success")
        return redirect(url_for('registromarcacion'))  # Redirige al historial de marcaciones

    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al registrar marcación: {e}")
        flash("Error al registrar marcación. Inténtalo de nuevo.", "error")
        return redirect(request.referrer)  # Redirige a la misma página
    
    
    
#################### CONTROLADOR PARA SALIR DEL SISTEMA   
@app.route('/logout')
def logout():
     # Elimina los datos de la sesión
    session.clear()
    flash('Has cerrado sesión correctamente.' , 'info')
    
    return redirect(url_for('home'))


# Desactivar caché en rutas protegidas
@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response