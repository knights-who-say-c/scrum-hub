# task.py

from scrumhub import database


def createIssue(form, projectID):
    issueType = form['issueType']
    title = form['title']
    description = form['description']
    label = form['label']
    assignee = form['assignee']
    dueDate = form['due']

    database.createIssue(issueType, title, description, label, assignee, dueDate, projectID)


def issueToHTML(task):
    print(task, flush=True)
    return "<div>" + str(task["id"]) + "<br/>" + \
           task["type"] + "<br/>" + \
           task["title"] + "<br/>" + \
           task["description"] + "<br/>" + \
           task["label"] + "<br/>" + \
           "<b>" + task["assignee"] + "</b>" + "<br/>" + \
           str(task["duedate"]) + "<br/> </div>"

def HTMLInjection():
        tasks = database.getTasks()
        htmlInject = ""
        for x in tasks:
                htmlInject += ("<p>" +  x[0] + "<br/>" +  x[1] + "<br/>" +  x[2] + "<br/>" +  x[3] + "<br/>" +  x[4] + "<br/>" + str(x[5]) + "<br/>" +  "</p>")
        return htmlInject