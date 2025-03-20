from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash
import sqlite3

from db import Database

app = Flask(__name__)
db = Database("database.db", reset=True)

@app.route("/")
def index():
    return render_template("index.html", message="Hei maailma!")

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
