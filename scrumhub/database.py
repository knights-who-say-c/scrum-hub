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

def getUploadedFiles():
    cur.execute("SELECT * FROM Uploads")
    res = cur.fetchall()
    return res

    
    
