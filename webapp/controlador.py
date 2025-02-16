from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from functools import wraps
from datetime import datetime, timedelta
from webapp import app
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

# Decorador para verificar si el usuario tiene un rol específico
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'error')
                return redirect(url_for('login'))
            if session.get('role') != required_role:
                flash('No tienes permiso para acceder a esta página.', 'error')
                return redirect(url_for('series'))  # Redirigir a una página sin restricciones
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
            # Verificar contraseña y estado del usuario
            stored_password = user['Contraseña']
    

            if stored_password==contraseña:
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
                    return redirect(url_for('reloj'))
                    
                    
            else:
                flash('Contraseña incorrecta', 'error')
        else:
            flash('Usuario no registrado', 'error')
    
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template("login.html", title="EG90 Login", message="Marcaciones", content=formatted_now)



@app.route('/reloj')
@login_required
def reloj():
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "reloj.html",
        title = "EG90 WebApp",
        message = "Marcacion ",
        content =  formatted_now)
    
    
@app.route('/marcaciones')
@login_required
def marcaciones():
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %I:%M:%S %p")
    return render_template(
        "marcaciones.html",
        title = "EG90 WebApp",
        message = "Marcacion ",
        content =  formatted_now)  
    
    
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