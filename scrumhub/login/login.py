from datetime import datetime
from datetime import date
from flask import *
import os
import psycopg2
from werkzeug.utils import secure_filename

from scrumhub.login import task


app = Flask(__name__)
app.secret_key = "testkey1"

DATABASE_URL = os.environ['DATABASE_URL']
database = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = database.cursor()
database.autocommit = True

cur.execute("CREATE TABLE IF NOT EXISTS testLogins (firstName text, lastName text, email text, password text)")
cur.execute("CREATE TABLE IF NOT EXISTS testUploads (fileName text, file bytea, extension text, simpleName text)")
cur.execute("CREATE TABLE IF NOT EXISTS testTasks (title text, description text, label text, assignee text, dueDate date)")

# session == user currently logged in's information
# session['email'] = ""

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

@app.route('/')
def index():
    return redirect("home", code=301)

@app.route('/home')
def home():
    return render_template("home.html", title = "Home Page")

@app.route('/duedate')
def duedate():
    
    cur.execute("SELECT * FROM testTasks")
    tasks = list(cur.fetchall())
    dued = []
    for i in tasks:
        if str(i[4]) not in dued:
            dued.append(str(i[4]))

    htmlInjectTasks = ""
    print(tasks)
    dued.sort(key=lambda date: datetime.strptime(date,'%Y-%m-%d'))
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    # for x in dued:
    #     htmlInjectTasks += ("<div>" +  x + "</div>")
    for i in dued:
        for x in tasks:
            if i == str(x[4]):
                if i <= today:
                    htmlInjectTasks += ("<div class=" + "due" + ">" +  x[0] + "<br/>" +  x[1] + "<br/>" +  x[2] + "<br/>" +  x[3] + "<br/>" +  str(x[4]) + "<br/>"  + "OverDued" + "</div>")
                else:
                    htmlInjectTasks += ("<div>" +  x[0] + "<br/>" +  x[1] + "<br/>" +  x[2] + "<br/>" +  x[3] + "<br/>" +  str(x[4]) + "<br/>"  +  "</div>")
    return render_template("duedate.html", title = "Due Dates Page", due = htmlInjectTasks)

@app.route('/newtask')
def newtask():
    return render_template("newtask.html", title = "Home Page")

@app.route('/submitNewTask', methods = ['POST'])
def handleNewTask():
    formData = request.form
    task.handleNewTask(formData, cur)
    return redirect("project", code=301)
    
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
    cur.execute("SELECT * FROM testUploads")
    uploadedFiles = cur.fetchall()
    htmlInject = ""
    for x in uploadedFiles:
        htmlInject += ("<p>" + x[3] + "." + x[2] + "</p>")

    cur.execute("SELECT * FROM testTasks")
    tasks = cur.fetchall()

    htmlInjectTasks = ""
    for x in tasks:
        htmlInjectTasks += ("<p>" +  x[0] + "<br/>" +  x[1] + "<br/>" +  x[2] + "<br/>" +  x[3] + "<br/>" +  str(x[4]) + "<br/>"  +  "</p>")
        # x[0] + "." + x[1] + "."  + x[2] + "." + x[3] + "."  + x[4] +
 
 
    cur.execute("SELECT * FROM testTasks")
    tasks = cur.fetchall()
 
    return render_template("project.html", title = "Project Page", btasks = htmlInjectTasks, files = htmlInject)


@app.route('/project/fileUpload')
def fileUpload():
    return render_template("fileUpload.html", title = "File Upload")

@app.route('/project/fileUploadRequest', methods = ['POST'])
def fileUploadRequest():
    if request.method == "POST":
        formData = request.form

        name = formData["filename"]
        name = escapeHTML(name)

        upload = request.files["file"]
        filename = secure_filename(upload.filename)
        upload = upload.read()

        extension = filename.split(".")[-1]

        cur.execute("INSERT INTO testUploads (fileName, file, extension, simpleName) VALUES(%s, %s, %s, %s)", (filename, upload, extension, name))
        cur.execute("SELECT * FROM testUploads where fileName = %s", (filename,))
        result = cur.fetchone()
        filePath = result[3] + "." + result[2]

        with open(filePath, "wb") as testFile:
            testFile.write(result[1])
        
    return project()

@app.route('/profile')
def profile():
    return render_template("profile.html", title = "Profile")

@app.route('/profileUpdater', methods = ['POST'])
def handleUpdate():
    if request.method == 'POST':
        formData = request.form
        
        first = formData['fname']
        last = formData['lname']
        email = formData['email']
        password = formData['password']
        passwordConfirm = formData['cpass']

        msg = ""

        if first: cur.execute("UPDATE testLogins SET firstName = (%s) WHERE email = (%s)",(first, session['email'],))
        if last: cur.execute("UPDATE testLogins SET lastName = (%s) WHERE email = (%s)",(last, session['email'],))

        if password:
            if not validPassword(password, passwordConfirm): msg += "Password and confirmation must be the same <br/>"
            else: cur.execute("UPDATE testLogins SET password = (%s) WHERE email = (%s)",(password, session['email'],))
        
        if email:
            if not validEmail(email): msg += "Email is not a valid address <br/>"
            else:
                cur.execute("UPDATE testLogins SET email = (%s) WHERE email = (%s)",(email, session['email'],))
                session['email'] = email

        if not msg:
            flash("Saved Changes!")
        else:
            flash(msg)
    
    return redirect("profile", code=301)
  
# app.run(host='0.0.0.0', port=8000)
# not necessary to run in container according to docker documentation

