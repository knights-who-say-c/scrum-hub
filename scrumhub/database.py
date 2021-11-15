# database.py

import os
import psycopg2
import sys

DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

db = psycopg2.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
cur = db.cursor()
db.autocommit = True

cur.execute("CREATE TABLE IF NOT EXISTS Logins (firstName text, lastName text, email text, password text)")
cur.execute("CREATE TABLE IF NOT EXISTS Uploads (fileName text, file bytea, extension text, simpleName text)")
cur.execute("CREATE TABLE IF NOT EXISTS Tasks (type text, title text, description text, label text, assignee text, dueDate date, pipeline text)")


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


def getIssues():
    cur.execute("SELECT * FROM Tasks")
    return cur.fetchall()


def getIssuesInPipeline(pipeline):
    cur.execute("SELECT * FROM Tasks WHERE pipeline = %s", (pipeline,))
    issues = cur.fetchall()
    return [rowToDict("tasks", row) for row in issues]


def moveToPipeline(issue, pipeline):
    cur.execute("UPDATE Tasks SET pipeline = %s WHERE id = %s", (pipeline, issue))


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


def createIssue(issueType, title, description, label, assignee, dueDate):
    cur.execute("INSERT INTO Tasks (type, title, description, label, assignee, dueDate, pipeline) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                (issueType, title, description, label, assignee, dueDate, "Backlog"))


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

def getTasks():
    cur.execute("SELECT * FROM Tasks")
    return cur.fetchall()