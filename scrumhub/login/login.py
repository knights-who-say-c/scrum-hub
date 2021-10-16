from flask import *

import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_URL = "postgres://wrwgrvzkfihtdb:bec460c350a6b77c2cd4bddd0484cdeef19b0a3a1a4660ae28e4b333936edcd0@ec2-34-233-187-36.compute-1.amazonaws.com:5432/dbdb4ogu09rgqg"
database = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = database.cursor()
database.autocommit = True

cur.execute("CREATE TABLE IF NOT EXISTS testLogins (firstName text, lastName text, email text, password text)")
cur.execute("CREATE TABLE IF NOT EXISTS testUploads (fileName text, file bytea, extension text, simpleName text)")



def escapeHTML(string):
    string = string.replace('&', "&amp;")
    string = string.replace('<', "&lt;")
    string = string.replace('>', "&gt;")

    return string

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

@app.route('/home')
def home():
    return render_template("home.html", title = "Home Page")

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

        cur.execute("SELECT email FROM testLogins WHERE email = %s", (email,))
        existing = cur.fetchone()

        if existing:
            msg = "Account already exists for " + email

        if not msg:
            cur.execute("INSERT INTO testLogins (firstName, lastName, email, password) VALUES(%s, %s, %s, %s)", (first, last, email, password))
            msg = "Account created for " + email
        
    return render_template("login.html", title = "Sign Up", feedback = msg)
@app.route('/crproject')
def crproject():
    return render_template("crproject.html", title = "Create New Project")

@app.route('/project')
def project():
    return render_template("project.html", title = "Project Page")

@app.route('/project/fileUpload')
def fileUpload():
    return render_template("fileUpload.html", title = "File Upload")

@app.route('/project/fileUploadRequest', methods = ['POST'])
def fileUploadRequest():
    if request.method == "POST":
        formData = request.form
        print(formData)
        print(request.files)

        name = formData["filename"]
        name = escapeHTML(name)

        f = request.files["file"]
        #filename = f.filename
        #print(upload)

        extension = ""
        print("Testing Database")

        cur.execute("INSERT INTO testUploads (fileName, file, extension, simpleName) VALUES(%s, %s, %s)", (upload.filename, upload, extension, name))
        cur.execute("SELECT * FROM testUploads where fileName = %s", (name,))
        result = cur.fetchone()
        print(result)
        filePath = result(3) + result(2)

        with open(filePath, "wb") as testFile:
            testFile.write(result(1))
        


    return project()

app.run(host='0.0.0.0', port=8000)
# not necessary to run in container according to docker documentation
