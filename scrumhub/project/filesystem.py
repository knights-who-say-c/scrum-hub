from flask import Flask, render_template, session
#
# from scrumhub.main import app
from scrumhub.db import project
#
#
# @app.route('/project/files/')
# @app.route('/project/files/<path:path>')
def load_project_dir(path=''):
    print('test ', path)
    proj = project.get_project(session['project_id'])
    cur = proj.cursor()
    cur.goto(path)

    return render_template('filesystem.html',
                           title="File Viewer",
                           cursor=cur)
