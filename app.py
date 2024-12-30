#Ejecutar el comando de abajo para instalar las dependencias
# pip install -r requirements.txt

import os
from flask import Flask, jsonify, request, render_template_string
from datetime import datetime
import mysql.connector

# Crear el objeto Flask
app = Flask(__name__)

# Definir la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuración de la base de datos
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')  # Cambia si MySQL está en otro host
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')  # Usuario de MySQL
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'AQUiCONTRASEÑA')  # Contraseña de MySQL
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'tareas_db')  # Nombre de la base de datos

# Conexión a la base de datos
mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)

# Inicializar la tabla de tareas
def init_db():
    cursor = mysql.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            descripcion TEXT,
            fecha_creacion DATETIME,
            completada BOOLEAN DEFAULT 0
        )
    ''')
    mysql.commit()
    cursor.close()

#HTML básica con diseño Bootstrap
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gestor de Tareas</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            padding: 20px;
        }
        .task-container {
            margin-top: 20px;
        }
        .task-card {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center my-4">Gestor de Tareas</h1>
        <form action="/crear_tarea" method="post" class="mb-4">
            <div class="mb-3">
                <label for="titulo" class="form-label">Título de la tarea</label>
                <input type="text" class="form-control" name="titulo" id="titulo" placeholder="Título" required>
            </div>
            <div class="mb-3">
                <label for="descripcion" class="form-label">Descripción</label>
                <textarea class="form-control" name="descripcion" id="descripcion" rows="3" placeholder="Descripción"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Agregar Tarea</button>
        </form>

        <h2>Lista de Tareas</h2>
        <div class="task-container">
    {% for tarea in tareas %}
    <div class="card task-card">
        <div class="card-body">
            <h5 class="card-title">{{ tarea[1] }}</h5>
            <p class="card-text"><strong>Descripción:</strong> {{ tarea[2] }}</p>
            <p class="card-text"><small class="text-muted">Fecha: {{ tarea[3] }}</small></p>
            {% if tarea[4] %}
                <span class="badge bg-success">Completada</span>
                <form action="/completar_tarea/{{ tarea[0] }}" method="post" style="display:inline;">
                    <button type="submit" class="btn btn-warning btn-sm">Quitar</button>
                </form>
            {% else %}
                <form action="/completar_tarea/{{ tarea[0] }}" method="post" style="display:inline;">
                    <button type="submit" class="btn btn-success btn-sm">Completar</button>
                </form>
            {% endif %}
            <form action="/eliminar_tarea/{{ tarea[0] }}" method="post" style="display:inline;">
                <button type="submit" class="btn btn-danger btn-sm">Eliminar</button>
            </form>
        </div>
    </div>
    {% endfor %}
</div>


        <p class="mt-4">Total de tareas: <strong>{{ total_tareas }}</strong></p>
    </div>
</body>
</html>
'''

# Rutas de la aplicación
@app.route('/')
def home():
    try:
        cursor = mysql.cursor()
        cursor.execute('SELECT * FROM tareas ORDER BY id DESC')
        tareas = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) FROM tareas')
        total_tareas = cursor.fetchone()[0]
        cursor.close()
        return render_template_string(HTML_TEMPLATE, tareas=tareas, total_tareas=total_tareas)
    except Exception as e:
        return f"Error al cargar las tareas: {e}"

@app.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    try:
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion', '')
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = mysql.cursor()
        cursor.execute('INSERT INTO tareas (titulo, descripcion, fecha_creacion) VALUES (%s, %s, %s)',
                       (titulo, descripcion, fecha_creacion))
        mysql.commit()
        cursor.close()
        return home()
    except Exception as e:
        return f"Error al crear la tarea: {e}"

@app.route('/completar_tarea/<int:id>', methods=['POST'])
def completar_tarea(id):
    try:
        cursor = mysql.cursor()
        cursor.execute('UPDATE tareas SET completada = NOT completada WHERE id = %s', (id,))
        mysql.commit()
        cursor.close()
        return home()
    except Exception as e:
        return f"Error al completar la tarea: {e}"

@app.route('/eliminar_tarea/<int:id>', methods=['POST'])
def eliminar_tarea(id):
    try:
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM tareas WHERE id = %s', (id,))
        mysql.commit()
        cursor.close()
        return home()
    except Exception as e:
        return f"Error al eliminar la tarea: {e}"

# Inicializar la base de datos y ejecutar la aplicación
if __name__ == '__main__':
    init_db()  # Crear la tabla si no existe
    app.run(debug=True, port=5000)
