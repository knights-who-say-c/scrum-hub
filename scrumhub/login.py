# login.py - Account registration, authentication, and profiles

from scrumhub import database

def validEmail(email):
    at = email.find("@")
    dot = email.find(".")
    return at != -1 and dot > at

def validPassword(password, confirm):
    length = len(password) > 6
    confirmation = password == confirm
    
    return length and confirmation

def authenticate(formData):
    email = formData["email"]
    if not database.userExists(email):
        return False

    return database.getAccount(email)[3] == formData["password"]

def register(formData):
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

def updateProfile(formData):
    formData = request.form
        
    first = formData['fname']
    last = formData['lname']
    email = formData['email']
    password = formData['password']
    passwordConfirm = formData['cpass']

    msg = "Saved Changes!"

    if first:
        database.updateProfile("firstName", first, session["email"])
    if last:
        database.updateProfile("lastName", last, session["email"])

    if password:
        if not validPassword(password, passwordConfirm):
            msg += "Password and confirmation must be the same <br/>"
        else:
            database.updateProfile("password", password, session["email"])
            
    if email:
        if not validEmail(email):
            msg += "Email is not a valid address <br/>"
        else:
            database.updateProfile("email", email, session["email"])
            session['email'] = email
    return msg
    

