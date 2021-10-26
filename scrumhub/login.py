# login.py

from scrumhub import database

def validEmail(email):
    at = email.find("@")
    dot = email.find(".")
    return at != -1 and dot > at

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

def authenticate(email, password):
    database.cur.execute("SELECT email FROM Logins WHERE email = %s", (email,))
    existing = database.cur.fetchone()
    print(existing)
    if not existing:
        return False

    database.cur.execute("SELECT * FROM logins WHERE email = %s", (email,))
    stored = database.cur.fetchone()[3]
    return stored == password

def handleRegister(formData):
    first = formData['firstName']
    last = formData['lastName']

    email = formData['email']
    password = formData['password']
    passwordConfirm = formData['passwordConfirm']

    msg = ""
    if not validPassword(password, passwordConfirm):
        msg += "Password and confirmation must be the same <br/>"

    if not validEmail(email):
        msg += "Email is not a valid address <br/>"

    database.cur.execute("SELECT email FROM Logins WHERE email = %s", (email,))
    existing = database.cur.fetchone()

    if existing:
        msg = "Account already exists for " + email

    if not msg:
        database.cur.execute("INSERT INTO Logins (firstName, lastName, email, password) VALUES(%s, %s, %s, %s)", (first, last, email, password))
        msg = "Account created for " + email

    return msg

def handleLogin(formData):
    email = formData['email']
    password = formData['password']
    return authenticate(email, password)
