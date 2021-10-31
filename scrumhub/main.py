# main.py

from flask import *
import psycopg2
from werkzeug.utils import secure_filename

from scrumhub import task
from scrumhub import login
from scrumhub import database

app = Flask(__name__)
app.secret_key = "testkey1"

def escapeHTML(string):
    string = string.replace('&', "&amp;")
    string = string.replace('<', "&lt;")
    string = string.replace('>', "&gt;")

    return string

def getDisplayName():
    displayName = "Not logged in"
    if 'displayName' in session:
        displayName = session['displayName']
    return displayName

def getEmail():
    email = ""
    if "email" in session:
        email = session["email"]
    return email

@app.route('/')
def indexPage():
    return redirect("home", code=301)

@app.route('/home')
def homePage():
    return render_template("home.html", name = getDisplayName())


@app.route('/login', methods = ['GET', 'POST'])
def loginPage():
    if request.method == "GET":
        return render_template("login.html", title = "Log In")
    elif request.method == "POST":
        formData = request.form
        if login.authenticate(formData):
            email = formData['email']
            session['email'] = email
            session['displayName'] = database.getFirstName(email)
            return redirect("home", code=301)
        else:
            return render_template("login.html", title = "Log In", feedback = "Invalid username and/or password combination")

@app.route('/register', methods = ["GET", "POST"])
def registrationPage():
    if request.method == "GET":
        return render_template("login.html", title = "Sign Up")
    elif request.method == 'POST':
        msg = login.register(request.form) 
        return render_template("login.html", title = "Sign Up", feedback = msg)    

@app.route('/crproject')
def createProjectPage():
    return render_template("crproject.html", title = "Create New Project", name = getDisplayName())

@app.route('/project')
def projectPage():
    uploadedFiles = database.getUploadedFiles()
    injectedFiles = ""
    for x in uploadedFiles:
        injectedFiles += ("<p>" + x[3] + "." + x[2] + "</p>")
    injectedTasks = task.HTMLInjection() 
    return render_template("project.html", title = "Project Page", btasks = injectedTasks, files = injectedFiles, name = getDisplayName())


@app.route('/project/fileUpload', methods = ["GET", "POST"])
def fileUploadPage():
    if request.method == "GET":
        return render_template("fileUpload.html", title = "File Upload")
    elif request.method == "POST":
        formData = request.form

        name = formData["filename"]
        name = escapeHTML(name)

        upload = request.files["file"]
        filename = secure_filename(upload.filename)
        upload = upload.read()

        extension = filename.split(".")[-1]

        database.uploadFile(filename, upload, extension, name)
        return redirect("/project", code=301)
    
@app.route("/project/newTask", methods = ["GET", "POST"])
def newTask():
    if request.method == "GET":
        return render_template("newTask.html", name = getDisplayName())
    elif request.method == "POST":
        task.createTask(request.form, database.cur)
        return redirect("/project", code=301)

@app.route('/profile', methods = ["GET", "POST"])
def profilePage():
    if request.method == "GET":
        return render_template("profile.html", title = "Profile")
    elif request.method == "POST":
        msg = login.updateProfile(request.form, session)
        flash(msg)
        return redirect("/profile", code=301)
    
  
# app.run(host='0.0.0.0', port=8000)
# not necessary to run in container according to docker documentation


