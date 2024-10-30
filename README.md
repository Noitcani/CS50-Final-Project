# Personality Quiz Creation Platform
- (CS50x Final Project) for YJ TEO


## Introduction
- Welcome to Qui-Ez!
- Create Qui-ezs and let your friends take them online!

## TLDR
- Web App for users to create, store, and edit quizes.
- Quizes have a unique code that can be given to participants, so they can complete them. Quizes are self-scoring.
- User account management, with persistence of quizes. Quizes can be created and editted by authors on log-in.

### MVC stack
- **Model**: SQLite3 for Database
- **View**: HTML/CSS + JavaScript with Jinja Templating
- **Controller**: Python Flask

## Learning Areas
### More Python + Flask
- Web App's main controller stack
- Setting up venv for app
- Figuring out `sqlite3` python library instead of using `cs50` helpers

## JavaScript and JQuery
- JQuery and more complex JavaScript functions for dynamic generation and manipulation of DOM elements

### More Bootstrap
- More Bootstrap elements usage throughout the creation of site front-end from scratch

### Using different hashing
- To generate relatively unique, but short and usable quiz code

### venv commands
- Explored `venv` for project
- To manage dependencies
- To allow for real-time Debug, for updating of Python Flask App on change
```powershell
set-executionpolicy -scope currentuser remotesigned
.\quiez_app\Scripts\activate
```