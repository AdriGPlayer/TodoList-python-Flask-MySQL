from flask import Flask, render_template, request, redirect, url_for, session
import config
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
# configuraciones a la base de datos
app.config['SECRET_KEY'] = config.HEX_SEC_KEY  # key
app.config['MYSQL_HOST'] = config.MYSQL_HOST  # Host
app.config['MYSQL_USER'] = config.MYSQL_USER  # user
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD  # Pass
app.config['MYSQL_DB'] = config.MYSQL_DB  # DataBase

mysql = MySQL(app)

# ruta principal


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# ruta de login


@app.route('/login', methods=['POST'])
def login():
    # obtenemos datos de formulario
    email = request.form['email']
    password = request.form['password']

    # creamos un cursor
    cur = mysql.connection.cursor()
    sql = 'SELECT * FROM users WHERE email = %s AND password = %s'  # consulta SQL
    values = (email, password)  # valores para SQL
    cur.execute(sql, values)  # Ejecuta la consulta y pasa los valores
    user = cur.fetchone()  # Trae un elemento
    cur.close()

    if user is not None:  # si tenemos informacion en user
        # tomamos datos del usuario con la secion
        session['email'] = email
        session['name'] = user[1]
        session['last_name'] = user[2]

        return redirect(url_for('tasks'))
    else:
        return render_template('index.html', message="Las credenciales no son correctas")

# ruta de tareas


@app.route('/tasks', methods=['GET'])
def tasks():
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tasks WHERE email = %s', [email])
    tasks = cur.fetchall()
    insertObjet = []
    columNames = [column[0] for column in cur.description]
    for record in tasks:
        insertObjet.append(dict(zip(columNames, record)))
    cur.close()
    return render_template('tasks.html', tasks=insertObjet)


@app.route('/logout')
def logout():
    session.clear()  # elimina las variables de secion
    return redirect(url_for('home'))


@app.route('/new_task', methods=['POST'])
def new_task():
    # tomamos los datos de la nueva tarea del formulario
    title = request.form['title']
    description = request.form['description']
    email = session['email']
    d = datetime.now()  # guardamos la fecha que se agrego la tarea
    dateTask = d.strftime("%Y-%m-%d %H:%M:%S")
    # si estan todos los datos
    if title and description and email:
        cur = mysql.connection.cursor()
        sql = 'INSERT INTO tasks (email, title, description, date_task) Values (%s, %s, %s, %s)'
        data = (email, title, description, dateTask)
        cur.execute(sql, data)
        cur.connection.commit()
    return redirect(url_for('tasks'))


@app.route('/new_user', methods=['POST'])
def new_user():
    name = request.form['name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    # si estan todos los datos
    if name and last_name and email and password:
        cur = mysql.connection.cursor()
        sql = 'INSERT INTO users (name, last_name, email, password) values(%s,%s,%s,%s)'
        data = (name, last_name, email, password)
        cur.execute(sql, data)
        cur.connection.commit()
    return redirect(url_for('tasks'))


@app.route('/delete_task', methods=['POST'])
def delete_task():
    cur = mysql.connection.cursor()
    id_task = request.form['id']
    sql = 'DELETE FROM tasks WHERE id = %s'
    data = (id_task,)
    cur.execute(sql, data)
    mysql.connection.commit()
    return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run(debug=True)
