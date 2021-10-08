from flask import *

import os
import psycopg2

app = Flask(__name__)

DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
DATABASE_URL = os.environ['DATABASE_URL']

''' These credentials are bound to change over time.
    Can't figure out Heroku's DATABASE_URL so this has to do.... '''

HOST = "ec2-34-233-187-36.compute-1.amazonaws.com"
DATABASE = "dbdb4ogu09rgqg"
USER = "wrwgrvzkfihtdb"
PORT = "5432"

#database = psycopg2.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='require')
database = psycopg2.connect(dbname = DATABASE, user = USER, password = DATABASE_PASSWORD, host = HOST, port = PORT)
cur = database.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS testLogins (firstName text, lastName text, email text, password text)")

def validEmail(email):
    at = email.find("@")
    dot = email.find(".")
    return at != -1 and dot > at

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

def authenticate(email, password):
   return False

@app.route('/login')
def login():
    return render_template("login.html", title = "Log In")

@app.route('/register')
def register():
    return render_template("login.html", title = "Sign Up")

@app.route('/loginRequest', methods = ['POST'])
def handleLogin():
   
    return render_template("login.html", title = "Log In", feedback = "Login not implemented yet")


@app.route('/registerRequest', methods = ['POST'])
def handleRegister():
    if request.method == 'POST':
        formData = request.form

        first = formData['firstName']
        last = formData['lastName']

        email = formData['email']
        password = formData['password']
        passwordConfirm = formData['passwordConfirm']

        msg = ""
        if not validPassword(password, passwordConfirm):
            msg += "Password and confirmation must be the same <br/>"

        if not validEmail(email):
            msg += "Email is not a valid address <br/>"

        if not msg:
            cur.execute("INSERT INTO testLogins (firstName, lastName, email, password) VALUES(%s, %s, %s, %s)", (first, last, email, password))
            msg = "Account created for " + email
        
    return render_template("login.html", title = "Sign Up", feedback = msg)


app.run()








