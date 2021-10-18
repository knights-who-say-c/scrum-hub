from flask import *
import os
import psycopg2

app = Flask(__name__)
app.secret_key = "testkey1"

DATABASE_URL = os.environ['DATABASE_URL']
database = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = database.cursor()
database.autocommit = True

cur.execute("CREATE TABLE IF NOT EXISTS testLogins (firstName text, lastName text, email text, password text)")

# session == user currently logged in's information
session['email'] = ""

def validEmail(email):
    at = email.find("@")
    dot = email.find(".")
    return at != -1 and dot > at

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

def authenticate(email, password):
   return False

@app.route('/login')
def login():
    return render_template("login.html", title = "Log In")

@app.route('/register')
def register():
    return render_template("login.html", title = "Sign Up")

@app.route('/profile')
def profile():
    return render_template("profile.html", title = "Profile")

@app.route('/profileUpdater', methods = ['POST'])
def handleUpdate():
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

        if not msg:
            flash("Saved Changes!")
        else:
            flash(msg)
    
    return redirect("profile", code=301)