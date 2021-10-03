from flask import *

import os
import psycopg2

app = Flask(__name__)

def validEmail(email):
    at = email.find("@")
    dot = email.find(".", start = at)
    return at != -1 and dot != -1

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

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

    return render_template("login.html", title = "Log In")


@app.route('/registerRequest', methods = ['POST'])
def handleRegister():
    if request.method == 'POST':
        formData = request.form

        name = (formData['firstName'], formData['lastName'])

        email = formData['email']
        password = formData['password']
        passwordConfirm = formData['passwordConfirm']

        feedback = ""
        if not validPassword(password, passwordConfirm):
            feedback += "Password and confirmation must be the same <br/>"

        if not validEmail(email):
            feedback += "Email is not a valid address <br/>"
        
    return render_template("login.html", title = "Sign Up", feedback = feedback)


# DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
db_config = os.environ['DATABASE_URL'] if 'DATABASE_URL' in os.environ else 'user=postgres password=password'

database = psycopg2.connect(db_config, sslmode='require')


print("Does this work?")

app.run(host='0.0.0.0', port=8000)


