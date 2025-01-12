# Qui-ez

#### Video Demo: https://youtu.be/ImrTKvzQCI8
#### Description:

# Introduction
- Welcome to Qui-Ez!
- Create Qui-ezs and let your friends take them online!

# TLDR
- Qui-ez is a WebApp for users to create, store, and edit quizes.
- Quizes have a unique code that can be given to participants, so they can complete them. Quizes are self-scoring.
- User account management, with persistence of quizes. Quizes can be created and editted by authors on log-in.

# MVC stack
- **Model**: SQLite3 for Database
- **View**: HTML/CSS + JavaScript with Jinja Templating
- **Controller**: Python Flask


# Features
## Homepage
- On accessing the Homepage, users are prompted to either log-in or create an account.
- Access to functionality is gated by user log-in, checked against whether a verified `Session` is present (`flask_session`).
- These access changes are reflected in what buttons are visible in the rendered HTML.

## Registration and Login
- Standard fare for user management system.
- Input checks are present here for registration, including checking to ensure valid `username` and matching passwords.
- On successful registration, user data is stored on SQLite3 Database `users` table. Passwords are stored as hashes.
- On successful log in, `index.html` is rendered again, but with expanded functionality of the site.

## Creating Quizes
- When creating quizzes, users are able name their quizzes, and add any number of desired questions.
- Each question will require one correct answer, and three wrong decoy options.
- Users are also allowed to delete questions
- The HTML template snippets for questions are generated and deleted dynamically via JavaScript.
- Checks are put in place to ensure that a valid quiz is created.
    - Quiz name must be present
    - There must at least be one complete quiz question.
    - Each quiz question must have 4 answer options.
- Upon submission, the quiz data is stored into the SQLite3 Database (quizes), and a unique quiz code is generated.

## User's Quiz List
- A logged in user will see the list of quizzes authored by them.
- There is then the option to `edit` or `delete` quizzes.
- The corresponding quiz code for each quiz can also be seen.

## Editting Quizzes
- When a quiz is selected for editting, the quiz data is retrieved from the SQLite3 DB and presented in a editable form.
- Users can then make changes to all fields of the quiz (i.e. quiz name, quiz questions, and the answer options).
- Saved changes for the quiz data will overwrite existing data in the SQLite3 DB.

## Doing Quizes
- Even without logging in, users are able to input Qui-ez code (generated upon quiz creation) to do quizzes that will automatically be scored
- With the quiz code inputted, the quiz data will be fetched from the Database, and questions displayed.
- The answer options for each question is randomised at point of creation.
- Upon submission of the answers, the quiz will be scored, with a summary page of correct/wrong answers displayed.

# Learning Areas

## More Python + Flask
- I expanded on my learning from CS50 through deeper application of Python (Flask), using it as my WebApp's backend.
- Instead of using `cs50` helper scripts, I figured out `sqlite3` python library for SQLite3 to reduce dependencies.

## JavaScript and JQuery
- I learnt JQuery and more complex JavaScript functions for dynamic generation and manipulation of DOM elements.
- For example, when a user requests to expand their quiz with more questions, JQuery is used to find a template snippet of a blank question and duplicate it. This is then appended to the HTML code, and paramters such as the question numbering automatically changed.
- When rendering quizes to be administered, JQuery also helps with the creation of the requisite number of HTML snippets based on quiz length, followed by the selection of fields to be populated with the corresponding data (e.g. Quiz name, quiz questions and answer options).

## Jinja
- I made use of Jinja templating features to create custom error messages from one base HTML.
    - This allows flexible displaying of different error messages by passing them as parameters to a helper function that renders the error page.

## More Bootstrap
- More Bootstrap elements usage throughout the creation of the site's front-end. Including Navbars, buttons, headers and footers etc.

## Using different hashing
- To generate relatively unique, but short and usable quiz code, I searched for a suitable hashing function.
- Eventually, I settled for Shake256 which results in a 6 character hash. I compromised on a higher (but still unlikely) chance of hash collision, for user friendliness (a longer input code is unwieldy).

## venv commands
- To manage my `pypi` libraries, I explored `venv` for project.
- I also allowed for real-time Debug in code, for live updates of changes I make to my Python Flask App.
