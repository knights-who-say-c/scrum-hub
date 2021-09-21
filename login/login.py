from flask import *

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template("login.html", title = "Log In")

@app.route('/register')
def register():
    return render_template("login.html", title = "Sign Up")

app.run(host='0.0.0.0', port=8000)
