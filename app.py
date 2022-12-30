# Store this code in 'app.py' file
 
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import shodan 
from datetime import datetime

app = Flask(__name__)
 
 
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ip_port'
app.run(debug=True)

mysql = MySQL(app)

SHODAN_API_KEY = "KZdfqujx50kc00BZ4CFtKgzgB9oPQYCm"
api = shodan.Shodan(SHODAN_API_KEY)
 
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('my_ips'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/dashboard') 
def dashboard():
    msg = 'Logged in successfully !'
    return render_template('dashboard.html', msg = msg)

@app.route('/my_ips') 
def my_ips():
    msg = 'My IP list'

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ip')
    ips = cursor.fetchall()
    #print(account)
    return render_template('ip_list.html', ips = ips)

@app.route('/add_my_ip') 
def add_my_ip():
    msg = 'My IP list'
    return render_template('add_my_ip.html', msg = msg)

@app.route('/save_my_ip', methods =['POST'])
def save_my_ip():
    ip = request.form['ip']
    user_id = session['id']
    port = '' 
    last_scanned = datetime.now()
    created_at = datetime.now()
    updated_at = datetime.now()
    msg = ''
    try:           
        host = api.host(ip)            
        ports = host.get('ports', [])
        if len(ports) == 0:
            port = ''#writer.writerow([ip, "No open ports"])
        else:
            port = ",".join(str(port) for port in ports) #writer.writerow([ip, ",".join(str(port) for port in ports)])
    except shodan.APIError as e:
        port = 'Error: {}'.format(e) #print('Error: {}'.format(e))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO ip VALUES (NULL, % s, % s, % s, % s, % s, % s)', (ip, user_id, port, last_scanned, created_at, updated_at))
    mysql.connection.commit()
    message = 'Ip added successfully'
    return redirect(url_for('my_ips', message=message))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)