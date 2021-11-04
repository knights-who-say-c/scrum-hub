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
                htmlInject += ("<p>" +  str(x[0]) + "<br/>" +  str(x[1]) + "<br/>" +  str(x[2]) + "<br/>" +  str(x[3]) + "<br/>" +  str(x[4]) + "<br/>"  + str(x[5]) + "<br/>" + "</p>")
        return htmlInject
      
    
