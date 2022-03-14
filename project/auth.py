#Importamos los módulos a usar de flask
from crypt import methods
from this import d
from flask import Blueprint, render_template, redirect, url_for, request, flash
#Importamos los módulos de seguridad para las funciones hash
from werkzeug.security import generate_password_hash, check_password_hash

#Importamos el método login_required de flask_security
from flask_security import login_required
#Importamos los métodos login_user, logout_user flask_security.utils
#########################################################################################
from flask_security.utils import login_user, logout_user, hash_password, encrypt_password
##########################################################################################
#Importamos el modelo del usuario
from . models import Product, User
#Importamos el objeto de la BD y userDataStore desde __init__
from . import db, userDataStore

#Creamos el BluePrint y establecemos que todas estas rutas deben estar dentro de /security para sobre escribir las vistas por omisión de flask-security.
#Por lo que ahora las rutas deberán ser /security/login y security/register
auth = Blueprint('auth', __name__, url_prefix='/security')

@auth.route('/login')
def login():
    return render_template('/security/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    #Consultamos si existe un usuario ya registrado con el email.
    user = User.query.filter_by(email=email).first()

    #Verificamos si el usuario existe
    #Tomamos el password proporcionado por el usuario lo hasheamos, y lo comparamos con el password de la base de datos.
    if not user or not check_password_hash(user.password, password):
    #if not user or not user.password==encrypt_password(password):
        #Si el usuario no existe o no coinciden los passwords
        flash('El usuario y/o la contraseña son incorrectos')
        return redirect(url_for('auth.login')) #Si el usuario no existe o el password es incorrecto regresamos a login
    
    #Si llegamos a este punto sabemos que el usuario tiene datos correctos.
    #Creamos una sessión y logueamos al usuario
    login_user(user, remember=remember)
    return redirect(url_for('auth.read'))


@auth.route('/register')
def register():
    return render_template('/security/register.html')

@auth.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    #Consultamos si existe un usuario ya registrado con el email.
    user = User.query.filter_by(email=email).first()

    if user: #Si se encontró un usuario, redireccionamos de regreso a la página de registro
        flash('El correo electrónico ya existe')
        return redirect(url_for('auth.register'))

    #Creamos un nuevo usuario con los datos del formulario.
    # Hacemos un hash a la contraseña para que no se guarde la versión de texto sin formato
    #new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    userDataStore.create_user(
        name=name, email=email, password=generate_password_hash(password, method='sha256')
    )
    #userDataStore.create_user(
        #name=name, email=email, password=encrypt_password(password)
    #)
    
    #Añadimos el nuevo usuario a la base de datos.
    #db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    #Cerramos la sessión
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/read')
@login_required
def read():
    data = []
    
    # get data
    
    data = Product.query.all()
    
    return render_template('security/read.html', data = data)

@auth.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        # form data
        img = request.form.get('img')    
        category = request.form.get('category')    
        description = request.form.get('description') 
        
        product = Product(category, description, img)
        
        db.session.add(product)
        db.session.commit()
        
        return redirect(url_for('auth.read'))
        
    return render_template('security/read.html')
