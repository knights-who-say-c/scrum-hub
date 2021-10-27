# database.py

import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
db = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = db.cursor()
db.autocommit = True

cur.execute("CREATE TABLE IF NOT EXISTS Logins (firstName text, lastName text, email text, password text)")
cur.execute("CREATE TABLE IF NOT EXISTS Uploads (fileName text, file bytea, extension text, simpleName text)")
cur.execute("CREATE TABLE IF NOT EXISTS Tasks (title text, description text, label text, assignee text, dueDate date)")

def createAccount(first, last, email, password):
    cur.execute("INSERT INTO Logins (firstName, lastName, email, password) VALUES(%s, %s, %s, %s)", (first, last, email, password))

def userExists(email):
    return getAccount(email) is not None
    
def getAccount(email):
    cur.execute("SELECT * FROM logins WHERE email = %s", (email,))
    return cur.fetchone()

def getFirstName(email):
    cur.execute("SELECT * FROM Logins WHERE email = %s", (email,))
    return cur.fetchone()[0]

def getTasks():
    cur.execute("SELECT * FROM Tasks")
    return cur.fetchall()

def uploadFile(filename, upload, extension, name):
    cur.execute("INSERT INTO testUploads (fileName, file, extension, simpleName) VALUES(%s, %s, %s, %s)", (filename, upload, extension, name))

def getUploadedFiles():
    cur.execute("SELECT * FROM Uploads")
    return cur.fetchall()

def updateProfile(category, newVal, email):
    cur.execute("UPDATE Logins SET %s = %s WHERE email = %s", (category, newVal, email))

def createTask(title, description, label, assignee, dueDate):
    cur.execute("INSERT INTO Tasks (title, description, label, assignee, dueDate) VALUES(%s, %s, %s, %s, %s)", (title, description, label, assignee, dueDate))
    
    
