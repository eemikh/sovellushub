import sqlite3

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import Database

app = Flask(__name__)
app.secret_key = "2d0428696ca1cfc52c25ab54228c171f"
db = Database("database.db", reset=True)

@app.route("/")
def index():
    return render_template("index.html", message="Hei maailma!")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    queryres = db.query("SELECT password FROM users WHERE username = ?", [username])

    if len(queryres) == 0:
        return "Virhe: käyttäjää ei löytynyt"

    hash = queryres[0][0]

    if check_password_hash(hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "Virhe: väärä tunnus tai salasana"

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "Virhe: salasanat eivät ole samat"

    hash = generate_password_hash(password1)

    try:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", [username, hash])
    except sqlite3.IntegrityError:
        return "Virhe: tunnus on jo varattu"

    return "Tunnus luotu"
