from flask import *
import os
import psycopg2
from werkzeug.utils import secure_filename
import smtplib
import ssl

def validEmail(email):
        at = email.find("@")
        dot = email.find(".")
        return at != -1 and dot > at

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

class Profile:
    def handleAddCollab(request, cur):
        port = 465  # for ssl
        password = "changethispassword"

        # Create a secure SSL context
        context = ssl.create_default_context()

        if request.method == 'POST':
            email = session['email']

            # create project functionality was never finished
            # no project to test it on
            # project_name = session['project_name']

            formData = request.form
            collab_email = formData['email']
            if validEmail(collab_email):
                cur.execute(
                    "SELECT email FROM testLogins WHERE email = %s", (collab_email,))
                existing = cur.fetchone()
                if existing:

                    # for now use this, obvious fault is that it will affect ALL repos w the same owner
                    cur.execute("UPDATE testProjects SET collaborators = array_append(collaborators, %s) WHERE projectid = %s AND owner = %s ",
                                (collab_email, str(session['projectid']), email,))
                    
                    # use this code when a project can be created
                    # cur.execute("UPDATE project SET contributors = array_append(array_field, %s) WHERE owner = %s AND name = %s",
                    #             (collab_email, email, project_name))
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    sender_email = "scrumhubwebapp@gmail.com"
                    server.login(sender_email, password)
                    server.sendmail(sender_email, collab_email,
                                    """\nSubject: [ScrumHub] Project invitation\n\n{}: has invited you to their repository on ScrumHub!""".format(email))


    def update(request, cur):
        if request.method == 'POST':
            formData = request.form
            
            first = formData['fname']
            last = formData['lname']
            email = formData['email']
            password = formData['password']
            passwordConfirm = formData['cpass']

            msg = ""

            if first: cur.execute("UPDATE testLogins SET firstName = (%s) WHERE email = (%s)",(first, session['email'],))
            if last: cur.execute("UPDATE testLogins SET lastName = (%s) WHERE email = (%s)",(last, session['email'],))

            if password:
                if not validPassword(password, passwordConfirm): msg += "Password and confirmation must be the same <br/>"
                else: cur.execute("UPDATE testLogins SET password = (%s) WHERE email = (%s)",(password, session['email'],))
            
            if email:
                if not validEmail(email): msg += "Email is not a valid address <br/>"
                else:
                    cur.execute("UPDATE testLogins SET email = (%s) WHERE email = (%s)",(email, session['email'],))
                    session['email'] = email