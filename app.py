import os
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, randompw, columns

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///npc.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pwhash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Validate inputs
        # Name, not empty and unique
        rows = db.execute("SELECT COUNT(name) FROM users WHERE name=?", request.form.get("username"))

        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Name, password, and confirm password fields are required. Please try again.")

        if len(rows) != 1:
            return apology("Username already in use, please try again.")

        # Password at least 8 characters long
        if len(request.form.get("password")) < 8:
            return apology("Please choose a password with at least 8 characters.")

        # Password and confirm match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and confirm password fields did not match.")

        # Ensure challenges and answers are not empty
        if not request.form.get("pwChallenge1") or not request.form.get("pwChallenge2") or not request.form.get("pwChallenge3") or not request.form.get("pwChallenge1answer") or not request.form.get("pwChallenge2answer") or not request.form.get("pwChallenge3answer"):
            return apology("Please fill in the 3 challenges and their answers in case your password is lost and you need to reset it.")

        # If pass validation
        # Create dictionary of challenges and their answers
        challenges = {
            request.form.get("pwChallenge1"): request.form.get("pwChallenge1answer"),
            request.form.get("pwChallenge2"): request.form.get("pwChallenge2answer"),
            request.form.get("pwChallenge3"): request.form.get("pwChallenge3answer")
        }
        # Convert dictionary of challenges to json, apparently you can't have a python dictionary as a value in a sql table
        challenges = json.dumps(challenges)

        # Hash password
        hash = generate_password_hash(request.form.get("password"),method='sha256',salt_length=16)

        # Insert inputs into users db
        db.execute("INSERT INTO users (name, pwhash, email, challenges) VALUES (?, ?, ?, ?)", request.form.get("username"), hash, request.form.get("email"), challenges)

        # Set the registered user as the logged in user and render /
        user = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))
        session["user_id"] = user[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure original password was submitted
        if not request.form.get("oldPassword") or not request.form.get("newPassword") or not request.form.get("confirmation"):
            return apology("Must provide all current password, new password, and confirm new password", 403)

        # Passwords should be 8 or more characters long
        elif len(request.form.get("newPassword")) < 8 or len(request.form.get("confirmation")) < 8:
            return apology("Passwords must contain 8 or more characters.")

        # Ensure new password and confirm password match
        elif request.form.get("newPassword") != request.form.get("confirmation"):
            return apology("New password and confirm passwords must match.")

        # Ensure new password does not match old password
        elif request.form.get("oldPassword") == request.form.get("newPassword"):
            return apology("New password can not be the same as old password.")
        print(request.form.get("oldPassword"))
        print(request.form.get("newPassword"))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pwhash"], request.form.get("oldPassword")):
            return apology("invalid password", 403)

        # Update DB with new password
        hash = generate_password_hash(request.form.get("newPassword"), method='sha256', salt_length=16)
        # Insert inputs into users db
        db.execute("UPDATE users SET pwhash=? WHERE id IS ?", hash, session["user_id"])
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")


@app.route("/resetpw", methods=["GET", "POST"])
def resetpw():
    """Page to reset password if forgotten, first step locate account"""
    if request.method == "POST":
        # Either the user name field or the email field must be filled in
        if not request.form.get("username") and not request.form.get("email"):
            return apology("To Reset the pw we need either the user name or the email address.")
        # Need to confirm that the user name or email entered are in the db
        namerows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))
        emailrows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        if len(namerows) != 1 and len(emailrows) != 1:
            return apology("Account not found. Try again or register for an account.")

        elif not request.form.get("username") and len(emailrows) == 1:
            # Get challenges from users table
            challengesjson = db.execute("SELECT challenges FROM users WHERE email=?", request.form.get("email"))
            # Pull our dict out of the list of dicts our query created
            ch = challengesjson[0]
            # Convert from Json to dict
            challenges = json.loads(ch["challenges"])
            # Trying to mitigate security risks by only sending the keys, I only want the server to pull the values.
            keys = challenges.keys()
            name = db.execute("SELECT name FROM users WHERE email=?", request.form.get("email"))
            return render_template("resetpwchallenge.html", keys=keys, name=name[0]["name"], email=request.form.get("email"))
        else:
            # Get challenges from users table
            challengesjson = db.execute("SELECT challenges FROM users WHERE name=?", request.form.get("username"))
            # Pull our dict out of the list of dicts our query created
            ch = challengesjson[0]
            # Convert from Json to dict
            challenges = json.loads(ch["challenges"])
            # Trying to mitigate security risks by only sending the keys, I only want the server to pull the values.
            keys = challenges.keys()
            email = db.execute("SELECT email FROM users WHERE name=?", request.form.get("username"))
            return render_template("resetpwchallenge.html", keys=keys, email=email[0]["email"], name=request.form.get("username"))
    return render_template("resetpw.html")


@app.route("/resetpwchallenge", methods=["POST"])
def resetpwchallenge():
    """Page to reset password if forgotten, step2 verify challenge question"""
    if request.method == "POST":
        # Get name from db and confirm the email address matches it, in case someone modified it and tried to submit with false info or something
        email = db.execute("SELECT email FROM users WHERE name=?", request.form.get("username"))
        name = db.execute("SELECT name FROM users WHERE email=?", request.form.get("email"))
        name = name[0]["name"]
        email = email[0]["email"]
        # Get the challenges from Db
        challenges = db.execute("SELECT challenges FROM users WHERE name=?", request.form.get("username"))
        # It's stored as a list of dicts, pulling the first dict out
        ch = challenges[0]["challenges"]
        ch = json.loads(ch)
        # Since I filled in this page's username and email from my POST from resetpw if either of these fields are blank shenanigans may have happened.
        if not request.form.get("username") or not request.form.get("email"):
            return apology("To Reset the pw we need either the user name or the email address.")
        # Making sure that the user name and email submitted match what I think they should, again in case of shenanigans
        elif request.form.get("username") != name or request.form.get("email") != email:
            return apology("Username and emails don't match our records.")

        # Check if the chosen challenge question's stored answer is the same as what they typed in for the answer
        if ch[request.form.get("challenge")] != request.form.get("answer"):
            return apology("Sorry the answer was incorrect.")
        else:
            # Challenge answered correctly so set pw to random pw and send user to password change screen
            pw = randompw()

            # Hash random pw
            hash = generate_password_hash(pw, method='sha256', salt_length=16)
            # Update DB with new password
            db.execute("UPDATE users SET pwhash=? WHERE name IS ?", hash, request.form.get("username"))

            # Notify user pw has been reset.
            flash('Password reset to ' + pw + ' Please note this password. You can reset it via the Change Password page upon log in.')
            return render_template("login.html")

    return render_template("resetpw.html")


## Everything below this needs to be completed
@app.route("/")
@login_required
def index():
    """main page with character sheet"""
    return apology("TODO")


@app.route("/importExport", methods=["GET", "POST"])
@login_required
def importExport():
    """Page to import or export characters"""
    return apology("TODO")

@app.route("/spells", methods=["GET", "POST"])
@login_required
def spells():
    """Page to Create, import, and or export spells"""
    # Get a list of column names for spells table, input table name, get back a list of names, empty list if no rows in db.
    table = columns('spells')

    return apology("TODO")

@app.route("/monsters", methods=["GET", "POST"])
@login_required
def monsters():
    """Page to Create, import, and or export monsters"""
    return apology("TODO")

@app.route("/feats", methods=["GET", "POST"])
@login_required
def feats():
    """Page to Create, import, and or export feats"""
    return apology("TODO")

@app.route("/features", methods=["GET", "POST"])
@login_required
def features():
    """Page to Create, import, and or export features and abilities"""
    return apology("TODO")

@app.route("/races", methods=["GET", "POST"])
@login_required
def races():
    """Page to Create, import, and or export races"""
    return apology("TODO")

@app.route("/equipment", methods=["GET", "POST"])
@login_required
def equipment():
    """Page to Create, import, and or export equipment"""
    return apology("TODO")

@app.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    """Page to Create, import, and or export spells"""
    return apology("TODO")

@app.route("/languages", methods=["GET", "POST"])
@login_required
def languages():
    """Page to Create, import, and or export languages"""
    return apology("TODO")