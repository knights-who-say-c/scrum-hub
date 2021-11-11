# task.py

from scrumhub import database

def createIssue(form):
    issueType = form['issueType']
    title = form['title']
    description = form['description']
    label = form['label']
    assignee = form['assignee']
    dueDate = form['due']

    database.createIssue(issueType, title, description, label, assignee, dueDate)


def issueToHTML(task):
    return "<div>" + str(task["id"]) + "<br/>" + \
           task["type"] + "<br/>" + \
           task["title"] + "<br/>" + \
           task["description"] + "<br/>" + \
           task["label"] + "<br/>" + \
           task["assignee"] + "<br/>" + \
           str(task["duedate"]) + "<br/> </div>"
