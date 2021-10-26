# task.py

def handleNewTask(formData, cur):
        title = formData['title']
        description = formData['description']
        label = formData['label']
        assignee = formData['assignee']
        dueDate = formData['due']
        

        cur.execute("INSERT INTO testtasks (title, description, label, assignee, dueDate) VALUES(%s, %s, %s, %s, %s)", (title, description, label, assignee, dueDate))
      
    
