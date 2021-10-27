# main.py

from flask import *
import psycopg2
from werkzeug.utils import secure_filename

from scrumhub import task
from scrumhub import login
from scrumhub import database
from scrumhub.database import getUploadedFiles


app = Flask(__name__)
app.secret_key = "testkey1"

def escapeHTML(string):
    string = string.replace('&', "&amp;")
    string = string.replace('<', "&lt;")
    string = string.replace('>', "&gt;")

    return string

@app.route('/')
def indexPage():
    return redirect("home", code=301)

@app.route('/home')
def homePage():
    displayName = "Not logged in"
    if 'displayName' in session:
        displayName = session['displayName']
    return render_template("home.html", name = displayName)

@app.route('/newtask')
def newTaskPage():
    return render_template("newtask.html", title = "New Task")

@app.route('/submitNewTask', methods = ['POST'])
def handleNewTask():
    formData = request.form
    task.handleNewTask(formData, database.cur)
    return redirect("project", code=301)
    
@app.route('/login', methods = ['GET', 'POST'])
def loginPage():
    if request.method == "GET":
        return render_template("login.html", title = "Log In")
    else:
        formData = request.form
        if login.authenticate(formData['email'], formData['password']):
            email = formData['email']
            session['email'] = email
            session['displayName'] = database.getFirstName(email)
            return redirect("home", code=301)
        else:
            return render_template("login.html", title = "Log In", feedback = "Invalid username and/or password combination")

@app.route('/register')
def registrationPage():
    return render_template("login.html", title = "Sign Up")

@app.route('/registerRequest', methods = ['POST'])
def handleRegister():
    if request.method == 'POST':
        formData = request.form
        msg = login.handleRegister(formData)
        
        return render_template("login.html", title = "Sign Up", feedback = msg)

@app.route('/crproject')
def createProjectPage():
    return render_template("crproject.html", title = "Create New Project")

@app.route('/project')
def projectPage():
    uploadedFiles = database.getUploadedFiles()
    htmlInject = ""
    for x in uploadedFiles:
        htmlInject += ("<p>" + x[3] + "." + x[2] + "</p>")

    htmlInjectFiles = task.HTMLInjection()    
 
    return render_template("project.html", title = "Project Page", btasks = htmlInjectTasks, files = htmlInject)


@app.route('/project/fileUpload')
def fileUploadPage():
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

        database.uploadFile(filename, upload, extension, name)
        
    return project()

@app.route('/profile')
def profilePage():
    return render_template("profile.html", title = "Profile")

@app.route('/profileUpdater', methods = ['POST'])
def handleProfileUpdate():
    if request.method == 'POST':
        formData = request.form
        
        first = formData['fname']
        last = formData['lname']
        email = formData['email']
        password = formData['password']
        passwordConfirm = formData['cpass']

        msg = ""

        if first:
            database.updateProfile("firstName", first, session["email"])
        if last:
            database.updateProfile("lastName", last, session["email"])

        if password:
            if not validPassword(password, passwordConfirm):
                msg += "Password and confirmation must be the same <br/>"
            else:
                database.updateProfile("password", password, session["email"])
                
        if email:
            if not validEmail(email): msg += "Email is not a valid address <br/>"
            
            else:
                database.updateProfile("email", email, session["email"])
                session['email'] = email

        if not msg:
            flash("Saved Changes!")
        else:
            flash(msg)
    
    return redirect("profile", code=301)
  
# app.run(host='0.0.0.0', port=8000)
# not necessary to run in container according to docker documentation


