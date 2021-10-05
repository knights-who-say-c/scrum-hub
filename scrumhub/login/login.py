from flask import *

app = Flask(__name__)

@app.route('/home')
def register():
    return render_template("home.html", title = "Home Page")

@app.route('/login')
def login():
    return render_template("login.html", title = "Log In")

@app.route('/register')
def home():
    return render_template("login.html", title = "Sign Up")

@app.route('/crproject')
def crproject():
    return render_template("crproject.html", title = "Sign Up")

# app.run(host='0.0.0.0', port=8000)
# line 13 not necessary to run in container
# according to docker documentation