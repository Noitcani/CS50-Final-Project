import requests
import sqlite3

from flask import redirect, render_template, session
from functools import wraps


def invalid_action(message, submessage, code=400):
    return render_template("invalid.html", message=message, submessage=submessage), code


def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def create_all_tables(cursor):
    # Create 'users' table.
    cursor.execute("CREATE TABLE IF NOT EXISTS users (\
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                        username TEXT NOT NULL,\
                        hash TEXT NOT NULL);")
    
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users(username);")

    cursor.execute("CREATE TABLE IF NOT EXISTS quizes (\
                        quiz_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                        quiz_name TEXT NOT NULL,\
                        number_of_questions INTEGER NOT NULL,\
                        quiz_dict TEXT NOT NULL,\
                        quiz_code TEXT NOT NULL,\
                        owner_id INTEGER NOT NULL,\
                        FOREIGN KEY (owner_id)\
                            REFERENCES users(user_id));")


def dict_from_row(row):
    return dict(zip(row.keys(), row))


def created_quiz_has_no_blanks(request_form_dict: dict):
    for key in request_form_dict:
        if request_form_dict[key] == "":
            return False
    return True


def process_create_form_dict(request_form_dict: dict):
    output_dict = {}
    number_of_questions = int((len(request_form_dict) - 1) / 5)
    
    output_dict['quiz_name'] = request_form_dict['quiz_name']
    output_dict['number_of_questions'] = number_of_questions
    
    for qs in range(number_of_questions):
        output_dict['q' + str(qs)] = {}
        output_dict['q' + str(qs)]['qs_text'] = request_form_dict['q' + str(qs) + 'qstext']
        output_dict['q' + str(qs)]['ans0'] = request_form_dict['q' + str(qs) + 'ans0']
        output_dict['q' + str(qs)]['ans1'] = request_form_dict['q' + str(qs) + 'ans1']
        output_dict['q' + str(qs)]['ans2'] = request_form_dict['q' + str(qs) + 'ans2']
        output_dict['q' + str(qs)]['ans3'] = request_form_dict['q' + str(qs) + 'ans3']
    return output_dict


def intraquestion_answers_are_unique(processed_dict):
    for key in processed_dict:
        if key not in ['quiz_name', 'number_of_questions']:
            for question in processed_dict[key]:
                answer_set = set([processed_dict[key]['ans0'], processed_dict[key]['ans1'], processed_dict[key]['ans2'], processed_dict[key]['ans3'],])
                if len(answer_set) < 4:
                    return False
    return True


def to_caps(data):
    return str(data).capitalize()