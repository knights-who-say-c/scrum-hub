from flask import Flask, render_template, session

from scrumhub.db import project

app = Flask(__name__)


@app.route('/project/files<path>')
def load_project_dir(path):
    proj = project.get_project(session['project_id'])
    cur = proj.cursor()
    cur.goto(path)

    return render_template("filesystem.html",
                           title="File Viewer",
                           dirnames=cur.subdir_names(),
                           filenames=cur.file_names())
