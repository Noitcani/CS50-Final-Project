from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
import json
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import create_all_tables, dict_from_row, invalid_action, login_required

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

connection = sqlite3.connect("./databases/quiez.db", check_same_thread=False)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# cursor.execute("DROP TABLE users;")
create_all_tables(cursor)
connection.commit()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if request.form.get("username") == "":
            return invalid_action("Invalid Log-in", "Must provide username", 401)

        # Ensure password was submitted
        elif request.form.get("password") == "":
            return invalid_action("Invalid Log-in", "Must provide password", 401)

        # Query database for username
        rows = cursor.execute("SELECT * FROM users WHERE username = :username;", request.form).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return invalid_action("Invalid Log-in", "Invalid username and/or password", 401)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        session["username"] = rows[0]["username"]

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
    if request.method == "POST":
        username_entered = request.form.get("username")
        password_entered = request.form.get("password")
        password_confirmation = request.form.get("confirmation")

        # Make sure username is not blank
        if username_entered == "":
            return invalid_action("Invalid Registration", "Username cannot be empty.")

        # Make sure password is not blank
        if password_entered == "" or password_confirmation == "":
            return invalid_action("Invalid Registration", "Password cannot be empty.")

        # Make sure password and confirmation match
        if password_entered != password_confirmation:
            return invalid_action("Invalid Registration", "Passwords do not match.")
        
        # Make sure username doesn't exists in DB
        try:
            cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?);", [username_entered, generate_password_hash(password_entered)])
            connection.commit()

        except sqlite3.IntegrityError:
            return invalid_action("Invalid Registration", "Username already exists.")

        return redirect("/")

    return render_template("/register.html")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        return redirect("/")
    return render_template("create.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
