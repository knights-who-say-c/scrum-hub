from flask import *
import os
import psycopg2
from werkzeug.utils import secure_filename
import smtplib
import ssl

class Profile:
    def update(request, cur):
        if request.method == 'POST':
            formData = request.form

            first = formData['fname']
            last = formData['lname']
            email = formData['email']
            password = formData['password']
            passwordConfirm = formData['cpass']

            msg = ""

            if first:
                cur.execute(
                    "UPDATE testLogins SET firstName = (%s) WHERE email = (%s)", (first, session['email'],))
            if last:
                cur.execute(
                    "UPDATE testLogins SET lastName = (%s) WHERE email = (%s)", (last, session['email'],))

            if password:
                if not login.validPassword(password, passwordConfirm):
                    msg += "Password and confirmation must be the same <br/>"
                else:
                    cur.execute("UPDATE testLogins SET password = (%s) WHERE email = (%s)", (password, session['email'],))

            if email:
                if not login.validEmail(email):
                    msg += "Email is not a valid address <br/>"
                else:
                    cur.execute(
                        "UPDATE testLogins SET email = (%s) WHERE email = (%s)", (email, session['email'],))
                    session['email'] = email
