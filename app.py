import hashlib
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
import json
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import create_all_tables, dict_from_row, invalid_action, login_required, created_quiz_has_no_blanks, process_create_form_dict, intraquestion_answers_are_unique, to_caps

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'

app.jinja_env.filters['to_caps'] = to_caps

Session(app)

connection = sqlite3.connect("./databases/quiez.db", check_same_thread=False)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# cursor.execute("DROP TABLE IF EXISTS users;")
# cursor.execute("DROP TABLE IF EXISTS quizes;")
# connection.commit()

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
    user_quizes = cursor.execute("SELECT * FROM quizes WHERE owner_id = ?;", [session["user_id"]]).fetchall()

    user_quizes_list = []
    for quiz in user_quizes:
        user_quizes_list.append({k: quiz[k] for k in quiz.keys()})

    # user_quizes = cursor.execute("SELECT * FROM quizes WHERE owner_id = ?;", session["user_id"])
    return render_template("index.html", user_quizes_list=user_quizes_list)


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
    if not session["user_id"]:
            return invalid_action("Unauthorized Access", "You need to be logged in")
    
    if request.method == "POST":
        if not created_quiz_has_no_blanks(request.form.to_dict()):
            return invalid_action("Invalid Quiz", "No Quiz field should be blank!")

        print(request.form.to_dict())
        form_dict = process_create_form_dict(request.form.to_dict())

        if not intraquestion_answers_are_unique(form_dict):
            return invalid_action("Invalid Quiz", "There was a repeated answer in one of the questions")


        quiz_name = form_dict["quiz_name"]
        number_of_questions = form_dict["number_of_questions"]
        quiz_dict = str(form_dict)
        quiz_hash = hashlib.shake_256(quiz_dict.encode()).hexdigest(3)
        print(quiz_hash)

        cursor.execute("INSERT INTO quizes (quiz_name, number_of_questions, quiz_dict, quiz_code, owner_id) VALUES(?, ?, ?, ?, ?);", [quiz_name, number_of_questions, quiz_dict, quiz_hash, session["user_id"]])
        connection.commit()

        return redirect("/")
    return render_template("create.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        quiz_code_to_delete = request.form.get("delete-quiz")
        cursor.execute("DELETE FROM quizes WHERE quiz_code = ?;", [quiz_code_to_delete])
        connection.commit()
    return redirect("/")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        quiz_code_to_edit = request.form.get("edit-quiz")
        session["editing_quiz_code"] = quiz_code_to_edit
        quiz_data = cursor.execute("SELECT * FROM quizes WHERE quiz_code = ?;", [quiz_code_to_edit]).fetchone()
        quiz_name = quiz_data["quiz_name"]
        number_of_questions = quiz_data["number_of_questions"]
        quiz_dict = quiz_data["quiz_dict"]
        quiz_dict = eval(quiz_dict)
        question_list = []
        for i in range(number_of_questions):
            question_list.append(quiz_dict["q" + str(i)])
        return render_template("edit.html", quiz_code_to_edit=quiz_code_to_edit, quiz_name=quiz_name, number_of_questions=number_of_questions, quiz_dict=quiz_dict)


@app.route("/save_changes", methods=["GET", "POST"])
@login_required
def save_changes():
    if not session.get("user_id"):
            return invalid_action("Unauthorized Access", "You need to be logged in")
    
    if not session.get("editing_quiz_code"):
        return invalid_action("Error", "No quiz selected for edit")

    if request.method == "POST":
        if not created_quiz_has_no_blanks(request.form.to_dict()):
            return invalid_action("Invalid Quiz", "No Quiz field should be blank!")

        print(request.form.to_dict())
        form_dict = process_create_form_dict(request.form.to_dict())

        if not intraquestion_answers_are_unique(form_dict):
            return invalid_action("Invalid Quiz", "There was a repeated answer in one of the questions")

        quiz_name = form_dict["quiz_name"]
        number_of_questions = form_dict["number_of_questions"]
        quiz_dict = str(form_dict)

        cursor.execute("UPDATE quizes SET quiz_name = ?, number_of_questions = ?, quiz_dict = ? WHERE quiz_code = ?;", [quiz_name, number_of_questions, quiz_dict, session["editing_quiz_code"]])
        connection.commit()

        session.pop("editing_quiz_code", None)

        return redirect("/")


@app.route("/input_code", methods=["GET", "POST"])
def input_code():
    if request.method == "POST":
        quiz_code_input = request.form.get("quiz_code")
        rows = cursor.execute("SELECT * FROM quizes WHERE quiz_code = ?;", [quiz_code_input]).fetchall()
        if len(rows) != 1:
            return invalid_action("Invalid Quiz Code", "No Qui-ez associated with Code Entered.")
        
        quiz_data = rows[0]
        quiz_name = quiz_data["quiz_name"]
        number_of_questions = quiz_data["number_of_questions"]
        quiz_dict = quiz_data["quiz_dict"]
        quiz_dict = eval(quiz_dict)
        question_list = []
        for i in range(number_of_questions):
            question_list.append(quiz_dict["q" + str(i)])
        return render_template("do.html", quiz_code_input=quiz_code_input, quiz_name=quiz_name, number_of_questions=number_of_questions, quiz_dict=quiz_dict)
        
    return render_template("input_code.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
