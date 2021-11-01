from flask import *
import os
import psycopg2
from werkzeug.utils import secure_filename
from scrumhub import addCollab
from scrumhub.profile import Profile

app = Flask(__name__)
app.secret_key = "testkey1"

DATABASE_URL = os.environ['DATABASE_URL']
database = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = database.cursor()
database.autocommit = True

cur.execute(
    "CREATE TABLE IF NOT EXISTS testLogins (firstName text, lastName text, email text, password text)")
cur.execute(
    "CREATE TABLE IF NOT EXISTS testUploads (fileName text, file bytea, extension text, simpleName text)")
cur.execute(
    "CREATE TABLE IF NOT EXISTS testProjects (projectid uuid, owner text, collaborators text[])")


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
    return render_template("home.html", title="Home Page")


@app.route('/login')
def login():
    return render_template("login.html", title="Log In")


@app.route('/register')
def register():
    return render_template("login.html", title="Sign Up")


@app.route('/loginRequest', methods=['POST'])
def handleLogin():

    return render_template("login.html", title="Log In", feedback="Login not implemented yet")


@app.route('/registerRequest', methods=['POST'])
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
            cur.execute("INSERT INTO testLogins (firstName, lastName, email, password) VALUES(%s, %s, %s, %s)",
                        (first, last, email, password))
            msg = "Account created for " + email

    return render_template("login.html", title="Sign Up", feedback=msg)


@app.route('/crproject')
def crproject():
    return render_template("crproject.html", title="Create New Project")


@app.route('/project')
def project():
    # # Temporary project creation
    # session['email'] = "sprint3@buffalo.edu"
    # session['projectid'] = uuid.uuid1()
    # cur.execute("INSERT INTO testProjects (projectid, owner) VALUES(%s, %s)", (str(
    #     session['projectid']), session['email'],))

    cur.execute("SELECT * FROM testUploads")
    uploadedFiles = cur.fetchall()
    htmlInject = ""
    for x in uploadedFiles:
        htmlInject += ("<p>" + x[3] + "." + x[2] + "</p>")

    print(htmlInject)

    return render_template("project.html", title="Project Page", files=htmlInject)


@app.route('/project/fileUpload')
def fileUpload():
    return render_template("fileUpload.html", title="File Upload")


@app.route('/project/fileUploadRequest', methods=['POST'])
def fileUploadRequest():
    if request.method == "POST":
        formData = request.form

        name = formData["filename"]
        name = escapeHTML(name)

        upload = request.files["file"]
        filename = secure_filename(upload.filename)
        upload = upload.read()

        extension = filename.split(".")[-1]

        cur.execute("INSERT INTO testUploads (fileName, file, extension, simpleName) VALUES(%s, %s, %s, %s)",
                    (filename, upload, extension, name))
        cur.execute(
            "SELECT * FROM testUploads where fileName = %s", (filename,))
        result = cur.fetchone()
        filePath = result[3] + "." + result[2]

        with open(filePath, "wb") as testFile:
            testFile.write(result[1])

    return project()


@app.route('/profile')
def profile():
    return render_template("profile.html", title="Profile")


@app.route('/profileUpdater', methods=['POST'])
def handleProfileUpdate():
    pfile = Profile
    pfile.update(request, cur)
    return redirect("profile", code=301)


@app.route('/addCollab', methods=['POST', 'GET'])
def handleAddCollab():
    addCollab.handleAddCollab(request, cur)
    return redirect("/project", code=301)
