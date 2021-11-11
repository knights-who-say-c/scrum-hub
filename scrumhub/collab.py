from flask import *
import os
import psycopg2
from werkzeug.utils import secure_filename
import smtplib
import ssl
import psycopg2 as pg

DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']


def validEmail(email):
    at = email.find("@")
    dot = email.find(".")
    return at != -1 and dot > at


def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm

    return length and confirmation


def handleAddCollab(request, cur):
    """Add a collaborator
    input:      request & cursor
    results:    collaborator's email appended to contributor array
                email is sent to collaborator
    """
    port = 465  # for ssl
    password = "changethispassword"

    # Create a secure SSL context
    context = ssl.create_default_context()

    if request.method == 'POST':
        email = session['email']
        formData = request.form
        collab_email = formData['email']
        if validEmail(collab_email):
            cur.execute("UPDATE public.project SET contributors = array_append(contributors, %s) WHERE id = %s AND owner = %s ",
                        (collab_email, str(session['project_id']), email,))

            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                sender_email = "scrumhubwebapp@gmail.com"
                server.login(sender_email, password)

                msg = """From: {}
                To: {}\n
                Subject: [ScrumHub] Project Invitation\n
                {} has invited you to their project on ScrumHub!.\n
                """.format(email, collab_email, email)

                server.sendmail(sender_email, collab_email, msg)


def get_collabs(project_id):
    sql_string = f"SELECT contributors FROM public.project WHERE id = '{project_id}'"
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
    conn.autocommit = True
    results = []

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)
                results = cur.fetchall()

    finally:
        conn.close()

    return results