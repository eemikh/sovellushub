import sqlite3

from flask import Flask, flash, redirect, render_template, request, session
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
    queryres = db.query("SELECT id, password FROM users WHERE username = ?", [username])

    if len(queryres) == 0:
        flash("Virhe: käyttäjää ei löytynyt")
        return redirect("/login")

    user_id, hash = queryres[0]

    if check_password_hash(hash, password):
        session["username"] = username
        session["user_id"] = user_id
        return redirect("/")
    else:
        flash("Virhe: väärä tunnus tai salasana")
        return redirect("/login")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        flash("Virhe: salasanat eivät ole samat")
        return redirect("/register")

    hash = generate_password_hash(password1)

    try:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", [username, hash])
    except sqlite3.IntegrityError:
        flash("Virhe: tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu")
    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    del session["username"]
    del session["user_id"]
    flash("Kirjauduttu ulos")
    return redirect("/")

@app.route("/create")
def create_page():
    return render_template("create.html")

@app.route("/create", methods=["POST"])
def create():
    if "username" not in session:
        return redirect("/", code=403)

    name = request.form["name"]
    source_link = request.form["source_link"]
    download_link = request.form["download_link"]
    description = request.form["description"]

    db.execute("INSERT INTO programs (author, name, source_link, download_link, description) VALUES (?, ?, ?, ?, ?)", [session["user_id"], name, source_link, download_link, description])

    return redirect("/")

