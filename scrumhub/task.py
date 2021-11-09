# task.py

from scrumhub import database
import sys


def createIssue(form):
    issueType = form['issueType']
    title = form['title']
    description = form['description']
    label = form['label']
    assignee = form['assignee']
    dueDate = form['due']

    database.createIssue(issueType, title, description, label, assignee, dueDate)


def issueToHTML(task):
    print(task)
    sys.stdout.flush()
    return "<div>" + task["type"] + "<br/>" + \
           task["title"] + "<br/>" + \
           task["description"] + "<br/>" + \
           task["label"] + "<br/>" + \
           task["assignee"] + "<br/>" + \
           str(task["duedate"]) + "<br/> </div>"
