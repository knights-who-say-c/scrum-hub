from flask import *

import os
import psycopg2

app = Flask(__name__)

DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
DATABASE_URL = os.environ['DATABASE_URL']

database = psycopg2.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='require')
cur = database.cursor()

cur.execute("CREATE DATABASE test IF test NOT EXIST")
cur.execute("USE test")
cur.execute("CREATE TABLE logins IF logins NOT EXIST")

app.run(host='0.0.0.0', port=8000)






def validEmail(email):
    at = email.find("@")
    dot = email.find(".", start = at)
    return at != -1 and dot != -1

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

def authenticate(email, password):
    pwd = cur.execute("SELECT password FROM logins WHERE email = %s", (email))
    return password == pwd

@app.route('/login')
def login():
    return render_template("login.html", title = "Log In")

@app.route('/register')
def register():
    return render_template("login.html", title = "Sign Up")

@app.route('/loginRequest', methods = ['POST'])
def handleLogin():
    if request.method == 'POST':
        formData = request.form

        email = formData['email']
        password = formData['password']

        msg = ""
        if authenticate(email, password):
            msg = "Hello, " + email
        else:
            msg = "Email and password do not match"

    return render_template("login.html", title = "Log In", feedback = msg)


@app.route('/registerRequest', methods = ['POST'])
def handleRegister():
    if request.method == 'POST':
        formData = request.form

        name = (formData['firstName'], formData['lastName'])

        email = formData['email']
        password = formData['password']
        passwordConfirm = formData['passwordConfirm']

        msg = ""
        if not validPassword(password, passwordConfirm):
            msg += "Password and confirmation must be the same <br/>"

        if not validEmail(email):
            msg += "Email is not a valid address <br/>"

        if not feedback:
            cur.execute("INSERT INTO logins(firstName, lastName, email, password) VALUES(%s %s %s %s)", (name[0], name[1], email, password))
            msg = "Account created for " + email
        
    return render_template("login.html", title = "Sign Up", feedback = msg)










