# task.py

def handleNewTask(formData, cur):
        title = formData['title']
        description = formData['description']
        label = formData['label']
        assignee = formData['assignee']
        dueDate = formData['due']
        
        database.createTask(title, description, label, assignee, dueDate)
      
    
