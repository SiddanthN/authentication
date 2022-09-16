from flask import Flask, render_template, redirect, request, session, url_for
from flask_session import Session
import mysql.connector
from datetime import datetime

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

user = 'root'
db = 'student'
pswd = ''
conn = mysql.connector.connect(host = "localhost", user = user, password = pswd, database = db)
cursor = conn.cursor()
cursor.reset()

@app.route("/")
def home():
    return render_template('index_login_logout.html')
    
@app.route("/login/", defaults = {'msg': ''})
@app.route("/login/<msg>")
def login(msg):
    return render_template('login.html', msg = msg)

@app.route("/auth", methods = ['GET', 'POST'])
def auth():
    msg = ''
    if request.method == 'POST' and (request.form['username'] and request.form['password']):
        username = request.form['username']
        password = request.form['password']
        # cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        pswd = cursor.fetchall()
        if pswd:
            if password == pswd[0][0]:
                session['username'] = username
                session['password'] = password
                session['in_record'] = datetime.now()
                return redirect(url_for('home'))
            else:
                msg = 'Invalid username or password. Check credentials'
                return redirect(url_for('login', msg = msg))
        else:
            msg = 'First lets get you signed up!'
            return redirect(url_for('signup', msg = msg))
    else:
        msg = 'Please provide credentials.'
        return redirect(url_for('login', msg = msg))

@app.route("/logout")
def signout():
    session.pop('username', default = None)
    session.pop('password', default = None)
    session['out_record'] = datetime.now()
    return redirect(url_for('home'))


@app.route("/signup/", defaults = {'msg': ''})
@app.route("/signup/<msg>")
def signup(msg):
    return render_template('signup.html', msg = msg)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST' and (request.form['username'] and request.form['password']):
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            cursor.execute("INSERT INTO users VALUES (%s, %s, %s)", (username, email, password,))
            conn.commit()
            rows_inserted = cursor.rowcount
            if rows_inserted:
                msg = 'Successfully signed up!'
                return redirect(url_for('login', msg = msg))
            else:
                return '<h3>Something is not working. Try again later.</h3>'
        except mysql.connector.Error as err:
            msg = 'A user with that username already exists!. Try another one.'
            msg = (msg + '\n' + str(err))
            return redirect(url_for('signup', msg = msg))
    else:
        return redirect(url_for('signup', msg = 'Enter credentials.'))

if __name__ == '__main__':
    app.run(debug=True)











