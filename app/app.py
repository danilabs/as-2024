import logging
import pwd
import random
import re
import subprocess
from flask import Flask, jsonify, request, abort
from functools import wraps
from werkzeug.security import generate_password_hash
import sqlite3
import uuid
import os

app = Flask(__name__)
db_path = 'users.db'

# Configuración del logging
log_dir = "/mnt/smb/logs"
log_file = os.path.join(log_dir, "app.log")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

SSH_KEY_PATH = '/mnt/smb/ssh/'
if not os.path.exists(SSH_KEY_PATH):
    os.makedirs(SSH_KEY_PATH)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Conexión a la base de datos SQLite
def get_db():
    conn = sqlite3.connect(db_path)
    return conn

# Crear la base de datos y tablas si no existen
def init_db():
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Base de datos '{db_path}' eliminada.")

    if not os.path.exists(db_path):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                username TEXT PRIMARY KEY,
                name TEXT,
                role TEXT,
                email TEXT,
                api_key TEXT,
                pin_code INT
            )
        ''')
        logging.info("Base de datos inicializada con éxito.")
        conn.commit()
        conn.close()

def populate_db():
    USERS = {
    "test": {"name": "Test", "role": "test", "email": "test@ascompany.local", "api_key": "2915e0d-a787-4a67-b178-f4760199ecea", "pin_code":random.randint(100000, 999999)},
    "john": {"name": "John Doe", "role": "dev", "email": "john@ascompany.local", "api_key":  str(uuid.uuid4()),"pin_code":random.randint(100000, 999999)},
    "alice": {"name": "Alice Doe", "role": "admin", "email": "alice@ascompany.local", "api_key": str(uuid.uuid4()), "pin_code":random.randint(100000, 999999)}
    }
    conn = get_db()
    cursor = conn.cursor()
    
    # Insertar los usuarios en la base de datos
    for username, user_info in USERS.items():
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, name, role, email, api_key)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, user_info['name'], user_info['role'], user_info['email'], user_info['api_key']))
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()

# Decorador para validar la API-KEY
def api_key_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        api_key = request.headers.get('API-KEY')
        if not api_key:
            abort(403, description="API-KEY required")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE api_key=?", (api_key,))
        user_data = cursor.fetchone()
        
        if not user_data:
            abort(403, description="Invalid API-KEY")
        
        return f(*args, **kwargs)

    return wrap

# Función auxiliar para obtener un usuario por API-KEY
def get_user_by_api_key(api_key):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, role, email FROM users WHERE api_key=?", (api_key,))
    return cursor.fetchone()

def get_user_by_api_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, role, email FROM users WHERE email=?", (email,))
    return cursor.fetchone()


# Endpoint para listar usuarios
@app.route('/user/list', methods=['GET'])
@api_key_required
def list_users():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, name, role, email FROM users")
        user_data = cursor.fetchall()
        
        if not user_data:
            abort(404, description="No users found")
        
        users = [{'username': user[0], 'role': user[2], 'email': user[3]} for user in user_data]
        logging.info(f"Usuarios devueltos: {users}")
        return jsonify(users)
    except Exception as e:
        logging.error(f"Error en la base de datos: {e}")
        abort(500, description="Internal Server Error")

# Endpoint para obtener información detallada de un usuario
@app.route('/user/info', methods=['GET'])
@api_key_required
def get_user_info():
    api_key = request.headers.get('API-KEY')
    user_data = get_user_by_api_key(api_key)
    
    if not user_data:
        abort(404, description="User not found or invalid API-KEY")
    
    return jsonify({
        'username': user_data[0],
        'name': user_data[1],
        'role': user_data[2],
        'email': user_data[3],
        'api_key': api_key
    })


# Endpoint para solicitar un PIN Code
@app.route('/request-api-key', methods=['POST'])
def request_api_key():
    logging.info(f"Solicitud recibida en '/request-api-key': {request.json}")
    email = request.json.get('email')
    if not email:
        logging.warning("Solicitud sin email proporcionado.")
        abort(400, description="Email is required")

    # Generar un PIN Code de 6 dígitos
    pin_code = str(random.randint(100000, 999999))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET pin_code=? WHERE email=?", (pin_code, email))
    conn.commit()
    
    if cursor.rowcount == 0:
        logging.warning(f"El email '{email}' no está registrado.")
        abort(404, description="Email not found")
    
    logging.info(f"PIN Code generado para el usuario con email: {email}. PIN: {pin_code}")
    return jsonify({'message': 'PIN Code generated. Please check your email.'})

# Endpoint para generar una API-KEY usando email y PIN
@app.route('/generate-api-key', methods=['GET'])
def generate_api_key():
    logging.info(f"Solicitud recibida en '/generate-api-key': {request.json}")
    email = request.json.get('email')
    pin_code = request.json.get('pin_code')
    if not email or not pin_code:
        logging.warning("Solicitud sin email o PIN Code proporcionado.")
        abort(400, description="Email and PIN Code are required")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pin_code FROM users WHERE email=? AND pin_code=?", (email,pin_code))
    record = cursor.fetchone()
    
    if not record or record[0] != pin_code:
        logging.warning(f"PIN Code inválido o no coincide para el email: {email}")
        abort(403, description="Invalid PIN Code or email")
    
    # Generar nueva API-KEY
    api_key = str(uuid.uuid4())
    cursor.execute("UPDATE users SET api_key=?, pin_code=NULL WHERE email=?", (api_key, email))
    conn.commit()
    if email != "alice@ascompany.local":
        logging.info(f"API-KEY generada para el usuario con email: {email}. API-KEY: {api_key}")
    return jsonify({'api_key': api_key})


# Función para crear un par de claves SSH
def generate_ssh_keypair(email, user_home=SSH_KEY_PATH):
    # Obtener el nombre de usuario del email
    username = email.split('@')[0]  # Asumir que el nombre de usuario es el prefijo del email

    # Verificar si el usuario existe en el sistema
    try:
        user_info = pwd.getpwnam(username)
    except KeyError:
        raise Exception(f"El usuario {username} no existe en el sistema.")
    
    # Directorio home del usuario
    ssh_dir = os.path.join(SSH_KEY_PATH, username, '.ssh')
    print(ssh_dir)

    # Crear el directorio .ssh si no existe
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=0o700)  # Asegurarse de que los permisos sean correctos
    
    # Crear el nombre del archivo basado en el email
    number = random.randint(100000, 999999)
    key_name = f"{username}_{number}_id_rsa"
    private_key_path = os.path.join(ssh_dir, key_name)
    public_key_path = f"{private_key_path}.pub"

    # Comando para generar una clave RSA de 2048 bits sin frase de contraseña
    keygen_command = [
        "ssh-keygen", "-t", "rsa", "-b", "2048", "-f", private_key_path, "-q", "-N", "", "-C", email
    ]
    
    # Ejecutar el comando para generar las claves
    subprocess.run(keygen_command, check=True)

    # Establecer permisos correctos en la clave privada y el directorio .ssh
    os.chmod(ssh_dir, 0o700)  # Asegurar que el directorio .ssh tenga permisos 700
    os.chmod(private_key_path, 0o600)  # Asegurar que la clave privada tenga permisos 600
    os.chmod(public_key_path, 0o644)  # La clave pública puede ser accesible de manera más amplia

    # Leer la clave pública generada
    with open(public_key_path, "r") as pub_key_file:
        public_key = pub_key_file.read().strip()

    print(f"Clave privada: {private_key_path}")
    print(f"Clave pública: {public_key}")

    return private_key_path, public_key


# Función que genera la clave SSH y la asocia con el usuario
@app.route('/ssh/generate', methods=['POST'])
@api_key_required
def generate_ssh_key():
    email = request.json.get('email')  # Recibimos el email como parámetro en la URL
    user_home = request.json.get('username')  # Recibimos el username como parámetro en la URL

    user_data = get_user_by_api_email(email)
    user_role = user_data[2]

    if user_role == "test":
        abort(400, description="Role not allowed")
    
    if not email:
        abort(400, description="Email is required")
    
    # Generar la clave SSH para el usuario
    try:
        private_key_path, public_key = generate_ssh_keypair(email, user_home)
        
        # Crear el usuario en el sistema y agregar la clave pública
        #create_user_and_add_key(email, public_key)
        
        return jsonify({
            'message': 'SSH key pair generated successfully',
            'private_key_path': private_key_path,
            'public_key': public_key
        })
    except Exception as e:
        abort(500, description=f"Error generating SSH key: {str(e)}")

# Error handling
@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': str(error)}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

# Inicializar la base de datos si no se ha hecho aún
init_db()
populate_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
