from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyodbc

app = Flask(__name__)

app.secret_key = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database setup
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=.;UID=sa;PWD=commonpw@5057')
cursor = conn.cursor()

cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'client_table')
    CREATE TABLE client_table (
        id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(255) NOT NULL,
        phone NVARCHAR(15) NOT NULL,
        email NVARCHAR(255) NOT NULL,
        message NVARCHAR(MAX) NOT NULL,
        date date NOT NULL,
        time time(7) NOT NULL
    )
''')

conn.commit()

cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'login_table')
    CREATE TABLE login_table (
        id INT PRIMARY KEY IDENTITY(1,1),
        username NVARCHAR(255) NOT NULL,
        password NVARCHAR(255) NOT NULL
    )
''')
conn.commit()


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM login_table WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and user[2] == password:
            user_obj = User(user[0])  # Assuming the 'id' is in the first position
            login_user(user_obj)
            return redirect(url_for('table'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/book', methods=['POST'])
def book():
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        message = request.form['message']
        date = request.form['date']
        time = request.form['time']

        cursor.execute('INSERT INTO client_table (name, phone, email, message, date, time) VALUES (?, ?, ?, ?, ?, ?)', (name, phone, email, message, date, time))
        conn.commit()


        return render_template('index.html')

@app.route('/contact')
def contact():
        return render_template('contact.html')



@app.route('/signup')
def signup():
        return render_template('signup.html')

@app.route('/sign', methods=['POST'])
def sign():
        username = request.form['username']
        password = request.form['password']

        cursor.execute('INSERT INTO login_table (username, [password]) VALUES (?, ?)', (username, password))
        conn.commit()


        return render_template('index.html')



@app.route('/table')
def table():
    cursor.execute('SELECT * FROM client_table ORDER BY id DESC')
    data = cursor.fetchall()

    return render_template('table.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
