# database.py

import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

db = psycopg2.connect(DATABASE_URL, sslmode='prefer')
cur = db.cursor()
db.autocommit = True

cur.execute("CREATE TABLE IF NOT EXISTS Logins (firstName text, lastName text, email text, password text)")
cur.execute("CREATE TABLE IF NOT EXISTS Uploads (fileName text, file bytea, extension text, simpleName text)")
cur.execute("CREATE TABLE IF NOT EXISTS Tasks (type text, title text, description text, label text, assignee text, dueDate date, pipeline text, id serial, project text)")


def createAccount(first, last, email, password):
    cur.execute("INSERT INTO Logins (firstName, lastName, email, password) VALUES(%s, %s, %s, %s)",
                (first, last, email, password))


def userExists(email):
    return getAccount(email) is not None


def getAccount(email):
    cur.execute("SELECT * FROM logins WHERE email = %s", (email,))
    return cur.fetchone()


def getFirstName(email):
    cur.execute("SELECT * FROM Logins WHERE email = %s", (email,))
    return cur.fetchone()[0]


def getIssues(projectID):
    cur.execute("SELECT * FROM Tasks WHERE project = %s", (projectID,))
    return cur.fetchall()


def getIssuesInPipeline(pipeline, projectID):
    cur.execute("SELECT * FROM Tasks WHERE pipeline = %s AND project = %s", (pipeline, projectID))
    issues = cur.fetchall()
    return [rowToDict("tasks", row) for row in issues]


def moveToPipeline(issue, pipeline, projectID):
    cur.execute("UPDATE Tasks SET pipeline = %s WHERE id = %s AND project=%s", (pipeline, issue, projectID))


def uploadFile(filename, upload, extension, name):
    cur.execute("INSERT INTO Uploads (fileName, file, extension, simpleName) VALUES(%s, %s, %s, %s)",
                (filename, upload, extension, name))


def getUploadedFiles():
    cur.execute("SELECT * FROM Uploads")
    files = cur.fetchall()
    retVal = [rowToDict("Uploads", result) for result in files]
    if retVal == [None]:
        return []
    return retVal


def updatePassword(newVal, email):
    cur.execute("UPDATE Logins SET password = %s WHERE email = %s", (newVal, email))


def updateFirstName(newVal, email):
    cur.execute("UPDATE Logins SET firstname = %s WHERE email = %s", (newVal, email))


def updateLastName(newVal, email):
    cur.execute("UPDATE Logins SET lastname = %s WHERE email = %s", (newVal, email))


def updateEmail(newVal, email):
    cur.execute("UPDATE Logins SET email = %s WHERE email = %s", (newVal, email))


def createIssue(issueType, title, description, label, assignee, dueDate, projectId):
    cur.execute("INSERT INTO Tasks (type, title, description, label, assignee, dueDate, pipeline, project) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                (issueType, title, description, label, assignee, dueDate, "Backlog", projectId))


def getColumns(table):
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table,))
    return cur.fetchall()


def rowToDict(table, row):
    columns = getColumns(table)
    retVal = {}

    for i in range(len(columns)):
        retVal[columns[i][0]] = row[i]

    if retVal != {}:
        return retVal
   
def getCollabs(project_id):
    cur.execute(f"SELECT contributors FROM public.project WHERE id = '{project_id}'")
    return cur.fetchall()