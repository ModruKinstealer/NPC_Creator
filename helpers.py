# Home of any helper functions
import string
import random

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps


# Stolen from CS50 Finance distribution code
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


# Stolen from CS50 Finance distribution code
def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Simple function to generate a string of letters and numbers, length 8
def random_pw():
    pool = string.ascii_lowercase + string.digits
    pw = ''
    for i in range(8):
        pw += random.choice(pool)
    return pw

# Function to get the column names of a SQL table
def columns(table):
    # Set CS50 to use npc.db
    db = SQL("sqlite:///npc.db")
    # Query DB's specified table
    col = db.execute("SELECT * FROM ? LIMIT 1", table)
    # If database is not empty
    if len(col) == 1:
        col = col[0].keys()
        names = []
        for i in col:
            names.append(i)
        return(names)
    # If table was empty return an empty list
    names = []
    return(names)