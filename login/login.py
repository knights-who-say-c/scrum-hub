from flask import *

app = Flask(__name__)

@app.route('/login')
def login():
    return send_file("static/login.html")

app.run(host='0.0.0.0', port=8000)
