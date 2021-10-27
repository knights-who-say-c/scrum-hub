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
    if not database.userExists(email):
        return False

    return database.getAccount[3] == password

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

    if database.userExists(email):
        msg = "Account already exists for " + email

    if not msg:
        database.createAccount(first, last, email, password)
        msg = "Account created for " + email

    return msg
