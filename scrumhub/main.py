# main.py
import base64
from base64 import b64encode
from datetime import datetime
from datetime import date
from datetime import *
from pathlib import PurePath
from io import BytesIO

from flask import *
import psycopg2
from werkzeug.utils import secure_filename
# import datetime
from scrumhub.db import project

from scrumhub import task
from scrumhub import login
from scrumhub import database
from scrumhub import collab
from scrumhub.project import filesystem

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
    return redirect("login", code=301)


@app.route('/home')
def homePage():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    if request.method == "GET":
        return render_template("login.html", title="Log In")
    elif request.method == "POST":
        formData = request.form
        if login.authenticate(formData):
            email = formData['email']
            session['email'] = email
            session['displayName'] = database.getFirstName(email)
            return redirect("home", code=301)
        else:
            return render_template("login.html", title="Log In",
                                   feedback="Invalid username and/or password combination")


@app.route('/register', methods=["GET", "POST"])
def registrationPage():
    if request.method == "GET":
        return render_template("login.html", title="Sign Up")
    elif request.method == 'POST':
        msg = login.register(request.form)
        return render_template("login.html", title="Sign Up", feedback=msg)


@app.route('/mytasks')
def mytasks():
    tasks = database.getIssues(session["project_id"])
    dued = []
    for i in tasks:
        if str(i[4]) not in dued:
            dued.append(str(i[5]))

    htmlInjectTasks = ""
    print(tasks)
    dued.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    # for x in dued:
    #     htmlInjectTasks += ("<div>" +  x + "</div>")
    for i in dued:
        for x in tasks:
            if i == str(x[5]):
                name = getDisplayName()
                if name == str(x[4]):
                    if i <= today:
                        htmlInjectTasks += ("<div class=" + "due" + ">" + "<h3>" + str(
                                session['projectName']) + "</h3>" + "<br/>" + str(x[0]) + "<br/>" + str(
                                x[1]) + "<br/>" + str(x[2]) + "<br/>" + str(x[3]) + "<br/>" + str(x[4]) + "<br/>" + str(
                                x[5]) + "<br/>" + "OverDued" + "</div>")
                    else:
                        htmlInjectTasks += ("<div class=" + "notdue" + ">" + "<h3>" + str(
                                session['projectName']) + "</h3>" + "<br/>" + str(x[0]) + "<br/>" + str(
                                x[1]) + "<br/>" + str(x[2]) + "<br/>" + str(x[3]) + "<br/>" + str(x[4]) + "<br/>" + str(
                                x[5]) + "<br/>" + "</div>")
    return render_template("mytasks.html", title="my Tasks Page", due=htmlInjectTasks)


@app.route('/duedate')
def duedate():
    tasks = database.getIssues(session["project_id"])
    dued = []
    for i in tasks:
        if str(i[4]) not in dued:
            dued.append(str(i[5]))

    htmlInjectTasks = ""
    print(tasks)
    dued.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    for i in dued:
        for x in tasks:
            if i == str(x[5]):
                if i <= today:
                    htmlInjectTasks += ("<div class=" + "due" + ">" + str(x[0]) + "<br/>" + str(x[1]) + "<br/>" + str(
                            x[2]) + "<br/>" + str(x[3]) + "<br/>" + str(x[4]) + "<br/>" + str(
                            x[5]) + "<br/>" + "OverDued" + "</div>")
                else:
                    htmlInjectTasks += (
                                "<div class=" + "notdue" + ">" + str(x[0]) + "<br/>" + str(x[1]) + "<br/>" + str(
                                x[2]) + "<br/>" + str(x[3]) + "<br/>" + str(x[4]) + "<br/>" + str(
                                x[5]) + "<br/>" + "</div>")
    return render_template("duedate.html", title="Due Dates Page", due=htmlInjectTasks)


@app.route('/crproject')
def createProjectPage():
    return render_template("crproject.html", title="Create New Project")


@app.route('/moveIssue', methods=["POST"])
def moveIssue():
    formData = request.form
    id = formData["id"]
    newPipeline = formData["newPipeline"]

    database.moveToPipeline(id, newPipeline, session["project_id"])
    return redirect("/project", code=301)


@app.route('/project/')
def projectPage():
    uploadedFiles = database.getUploadedFiles()
    injectedFiles = ""

    for f in uploadedFiles:
        injectedFiles += ("<p>" + f["simplename"] + "." + f["extension"] + "</p>")

    pipelines = ["Backlog", "Planned", "In Progress", "Testing", "Completed", "Closed"]
    IssueHTML = {}

    for pipeline in pipelines:
        pipelineHTML = ""
        for issue in database.getIssuesInPipeline(pipeline, session["project_id"]):
            pipelineHTML += task.issueToHTML(issue) + "<br/>"
        IssueHTML[pipeline] = pipelineHTML

    # rendering the list of collaborators depends on session['project_id']
    htmlInjectCollabs = ""
    collabs = collab.get_collabs(session['project_id'])
    for x in collabs[0][0]:
        htmlInjectCollabs += ("<p>" + x + "</p> <br/>")

    return render_template("project.html", title="Project Page", backlog=IssueHTML["Backlog"],
                           planned=IssueHTML["Planned"],
                           inProgress=IssueHTML["In Progress"], testing=IssueHTML["Testing"],
                           completed=IssueHTML["Completed"],
                           closed=IssueHTML["Closed"], files=injectedFiles, name=getDisplayName(),
                           collaborators=htmlInjectCollabs)


@app.route('/project/files/')
@app.route('/project/files/<path:path>')
def load_project_dir(path=''):
    proj = project.get_project(session['project_id'])
    path = PurePath(path)
    cur = proj.cursor()

    if path.suffix:
        return redirect('/project/download/' + str(path))

    try:
        cur.goto(path)

    except FileNotFoundError:
        return abort(404, 'The requested file was not found on the server.')

    return render_template('filesystem.html',
                           title="File Viewer",
                           cursor=cur)


@app.route('/project/download/<path:path>')
def download_project_file(path=''):
    proj = project.get_project(session['project_id'])
    path = PurePath(path)
    cur = proj.cursor()
    cur.goto(path.parent)

    try:
        metadata = proj.get_file(str(path))
        file_data = metadata.get('fileContent')
        file = BytesIO(file_data)
        file.name = path.name

    except FileNotFoundError:
        return abort(404, 'The requested file was not found on the server.')

    return send_file(file, as_attachment=True, download_name=path.name)


@app.route('/projectCreate', methods=["GET", "POST"])
def projectCreate():
    if request.method == 'POST':
        formData = request.form
        session['project_id'] = project.create_project(formData['projectName'], session['email'], [])
        session['projectName'] = formData['projectName']
        print(session['project_id'])
        return redirect("project", code=301)


@app.route('/project/fileUpload', methods=["GET", "POST"])
def fileUploadPage():
    if request.method == "GET":
        return render_template("fileUpload.html", title="File Upload")

    if request.method == "POST":
        formData = request.form

        name = formData["filename"]
        name = escapeHTML(name)
        # Get the file as a FileStorage object
        upload = request.files["file"]
        # Save the filename securely (strip whitespaces, etc.)
        filename = secure_filename(upload.filename)
        # Encode the file to bytes before uploading to AWS repo
        upload = upload.read()
        # Get the project from the current user session
        proj = project.get_project(session['project_id'])
        # Put the file in the repo
        proj.put_file(upload, name)
        # Redirect back to project homepage
        return redirect("/project", code=301)


@app.route("/project/newTask")
def newTask():
    return redirect("/project/newIssue", code=301)


@app.route("/project/newIssue", methods=["GET", "POST"])
def newIssue():
    if request.method == "GET":
        return render_template("newtask.html")
    if request.method == "POST":
        task.createIssue(request.form, session["project_id"])
        return redirect("/project", code=301)


@app.route('/profile', methods=["GET", "POST"])
def profilePage():
    if request.method == "GET":
        return render_template("profile.html", title="Profile")
    if request.method == "POST":
        msg = login.updateProfile(request.form, session)
        flash(msg)
        return redirect("/profile", code=301)


@app.route('/addCollab', methods=['POST', 'GET'])
def handleAddCollab():
    collab.handleAddCollab(request, database.cur)
    return redirect("/project", code=301)


@app.route('/my_projects')
def handle_my_projects():
    my_projects = project.get_my_projects(session['email'])
    injected_projects = []
    for proj in my_projects:
        injected_projects.append((proj.name, proj.uuid))
    return render_template("myprojects.html", title="My Projects", len=len(injected_projects),
                           Projects=injected_projects)


@app.route('/open_project', methods=['POST'])
def open_project():
    session['project_id'] = request.form['uuid']
    return redirect("/project", code=301)

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('email', None)
   return redirect("/login", code=301)
