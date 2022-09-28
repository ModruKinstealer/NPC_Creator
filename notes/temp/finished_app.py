import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Query which stocks are owned
    stocks = db.execute("SELECT symbol, price, SUM(qty) FROM transactions WHERE id = ? GROUP BY symbol", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])
    cash = cash[0]["cash"]
    stockvalue = float(0)
    # Add to stocks dictionaries the total for each symbol
    for stock in stocks:
        price = float(lookup(stock["symbol"])["price"])
        stockvalue += (float(stock["SUM(qty)"]) * price)
        stock["total"] = usd(stock["SUM(qty)"] * price)
        stock["price"] = usd(price)
        stock["shares"] = stock["SUM(qty)"]
        stock.pop("SUM(qty)")
        stockname = lookup(stock["symbol"])
        stock["name"] = stockname["name"]
    # Remove stocks with a "shares" < 1 from index page
    ownedStocks = []
    for stock in stocks:
        if stock["shares"] > 0:
            ownedStocks.append(stock)
    # Send to index.html so that Jinja can spit out a table
    stockvalue += cash
    stockvalue = usd(stockvalue)
    return render_template("index.html", stocks=ownedStocks, stockvalue=stockvalue, cash=usd(cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Get stock info and how much cash the logged in user currently has
        symbol = lookup(request.form.get("symbol"))
        cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])
        cash = cash[0]["cash"]

        # Validate Symbol
        if symbol is None:
            # Lookup un-successful (symbol is invalid)
            return apology("Symbol not found")
        # Check if all characters in shares are numeric
        elif not request.form.get("shares").isnumeric():
            return apology("Qty field must contain only numbers.")
        # Check if enough cash for purchase
        elif (float(request.form.get("shares")) * symbol["price"]) > cash:
            return apology("Not enough funds for purchase.")
        elif float(request.form.get("shares")) < 1:
            return apology("Qty must be a whole number greater than 0")
        elif float(request.form.get("shares")) % 1 != 0:
            return apology("Qty must be a whole number.")
        else:
            # Update DB with symbol, price, and qty of purchased shares
            # Get userid with session["user_id"]
            date = datetime.datetime.now()
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            db.execute("INSERT INTO transactions (id, symbol, qty, price, trans_type, time) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], symbol["symbol"], request.form.get("shares"), symbol["price"], "b", date)
            # Updates current cash amount after purchase
            cash = cash - float(request.form.get("shares")) * symbol["price"]
            db.execute("UPDATE users SET cash=? WHERE id IS ?", cash, session["user_id"])
            flash(str(request.form.get("shares")) + " Shares of " + symbol["symbol"] + " purchased.")
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # query db for all transactions of the logged in user
    stocks = db.execute("SELECT symbol, price, qty, time FROM transactions WHERE id = ?", session["user_id"])
    for stock in stocks:
        stock["name"] = lookup(stock["symbol"])["name"]
    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = lookup(request.form.get("symbol"))
        if symbol is None:
            # Lookup un-successful (symbol is invalid)
            return apology("Symbol not found")
        else:
            # Lookup successful (symbol is valid)
            return render_template("quoted.html", name=symbol["name"], price=usd(symbol["price"]), symb=symbol["symbol"])
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Validate inputs
        # Name, not empty and unique
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Name, password, and confirm password fields are required. Please try again.")
        if len(rows) > 0:
            return apology("Username already in use, please try again.")
        # Password and confirm match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and confirm password fields did not match.")
        # If pass validation
        # Hash password
        hash = generate_password_hash(request.form.get("password"), method='sha256', salt_length=16)
        # Insert inputs into users db
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)
        # Set the registered user as the logged in user and render /
        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = user[0]["id"]
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please select a stock to sell.")
        symbol = request.form.get("symbol")
        qtySold = int(request.form.get("shares"))
        currentPrice = lookup(symbol)["price"]
        stocks = db.execute("SELECT symbol, SUM(qty) FROM transactions WHERE id = ? AND symbol=? GROUP BY symbol",
                            session["user_id"], symbol)
        if qtySold > stocks[0]["SUM(qty)"]:
            return apology("You do not own that many shares")
        elif stocks[0]["SUM(qty)"] < 1:
            return apology("You do not own any shares of that stock")
        # Insert into transactions with bought qty a negative number
        else:
            date = datetime.datetime.now()
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            dbQtySold = 0 - qtySold
            # Insert into transactions table
            db.execute("INSERT INTO transactions (id, symbol, qty, price, trans_type, time) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], symbol, dbQtySold, currentPrice, "s", date)
            # Update user's cash value
            cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])
            cash = cash[0]["cash"] + (currentPrice * qtySold)
            db.execute("UPDATE users SET cash=? WHERE id IS ?", cash, session["user_id"])
            flash(str(qtySold) + " Shares of " + symbol + " sold.")
            return redirect("/")
    else:
        ownedStocks = db.execute("SELECT symbol, SUM(qty) FROM transactions WHERE id = ? GROUP BY symbol", session["user_id"])
        qtyOver1 = []
        for stock in ownedStocks:
            currentPrice = lookup(stock["symbol"])["price"]
            stock["price"] = usd(currentPrice)
            stock["qty"] = stock["SUM(qty)"]
            # Removing stocks that qty is less than 1 since we don't want/cant sell 0 or less stocks
            if stock["qty"] > 0:
                qtyOver1.append(stock)
        return render_template("sell.html", qtyOver1=qtyOver1)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("oldPassword"):
            return apology("Must provide all current password, new password, and confirm new password", 403)

        # Ensure password was submitted
        elif not request.form.get("newPassword"):
            return apology("Must provide all current password, new password, and confirm new password", 403)

        elif not request.form.get("confirmation"):
            return apology("Must provide all current password, new password, and confirm new password", 403)

        # Ensure new password and confirm password match
        elif request.form.get("newPassword") != request.form.get("confirmation"):
            return apology("New password and confirm passwords must match.")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("oldPassword")):
            return apology("invalid password", 403)

        # Update DB with new password
        hash = generate_password_hash(request.form.get("newPassword"), method='sha256', salt_length=16)
        # Insert inputs into users db
        db.execute("UPDATE users SET hash=? WHERE id IS ?", hash, session["user_id"])
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")