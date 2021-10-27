# task.py

from scrumhub import database

def createTask(formData, cur):
        title = formData['title']
        description = formData['description']
        label = formData['label']
        assignee = formData['assignee']
        dueDate = formData['due']
        
        database.createTask(title, description, label, assignee, dueDate)

def HTMLInjection():
        tasks = database.getTasks()
        htmlInject = ""
        for x in tasks:
                htmlInject += ("<p>" +  x[0] + "<br/>" +  x[1] + "<br/>" +  x[2] + "<br/>" +  x[3] + "<br/>" +  str(x[4]) + "<br/>"  +  "</p>")
        return htmlInject
      
    
