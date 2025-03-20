import sqlite3
import markupsafe

from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import Database

app = Flask(__name__)
app.secret_key = "2d0428696ca1cfc52c25ab54228c171f"
db = Database("database.db")

@app.route("/")
def index():
    # TODO: pagination
    programs = db.query("SELECT p.id, p.name, p.description, u.username FROM programs p, users u where u.id = p.author order by p.id desc")
    programs = [{"id": p[0], "name": p[1], "description": p[2], "author_name": p[3]} for p in programs]

    return render_template("index.html", programs=programs)

@app.route("/search")
def search():
    if "text" not in request.args:
        return redirect("/")

    searchtext = request.args["text"]

    # TODO: pagination
    programs = db.query("SELECT p.id, p.name, p.description, u.username FROM programs p, users u where u.id = p.author and (p.name like ? or p.description like ?) order by p.id desc", ["%" + searchtext + "%", "%" + searchtext + "%"])
    programs = [{"id": p[0], "name": p[1], "description": p[2], "author_name": p[3]} for p in programs]

    return render_template("search.html", programs=programs)

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

    program_id = db.execute("INSERT INTO programs (author, name, source_link, download_link, description) VALUES (?, ?, ?, ?, ?)", [session["user_id"], name, source_link, download_link, description])

    return redirect(f"/p/{program_id}")

@app.route("/p/<int:program_id>")
def program_page(program_id):
    try:
        name, author_name, author_id, source_link, download_link, description, program_id = db.query("SELECT p.name, u.username, u.id, p.source_link, p.download_link, p.description, p.id FROM programs p, users u WHERE p.author = u.id and p.id = ?", [program_id])[0]
    except IndexError:
        flash("Sovellusta ei löytynyt")
        return redirect("/", 404)

    reviews = db.query("SELECT r.grade, r.comment, u.username FROM users u, programs p LEFT JOIN reviews r ON r.program = p.id WHERE u.id = r.author and p.id = ?", [program_id])
    reviews = [{"grade": r[0], "comment": r[1], "username": r[2]} for r in reviews]

    can_review = "user_id" in session

    return render_template("program.html", name=name, author_name=author_name, author_id=author_id, source_link=source_link, download_link=download_link, description=description, program_id=program_id, can_review=can_review, reviews=reviews)

@app.route("/p/<int:program_id>/edit")
def program_edit_page(program_id):
    try:
        name, source_link, download_link, description, program_id = db.query("SELECT p.name, p.source_link, p.download_link, p.description, p.id FROM programs p, users u WHERE p.author = u.id and p.id = ?", [program_id])[0]
    except IndexError:
        flash("Sovellusta ei löytynyt")
        return redirect("/", 404)

    return render_template("edit.html", name=name, source_link=source_link, download_link=download_link, description=description, program_id=program_id)

@app.route("/p/<int:program_id>/edit", methods=["POST"])
def program_edit(program_id):
    if "username" not in session:
        return redirect("/", code=403)

    name = request.form["name"]
    source_link = request.form["source_link"]
    download_link = request.form["download_link"]
    description = request.form["description"]

    db.execute("UPDATE programs SET name = ?, source_link = ?, download_link = ?, description = ? WHERE id = ? and author = ?", [name, source_link, download_link, description, program_id, session["user_id"]])

    return redirect(f"/p/{program_id}")

@app.route("/p/<int:program_id>/delete", methods=["POST"])
def delete_program(program_id):
    if "user_id" not in session:
        return redirect("/", 404)

    db.execute("DELETE FROM programs WHERE id = ? AND author = ?", [program_id, session["user_id"]])

    return redirect ("/")

@app.route("/p/<int:program_id>/review", methods=["POST"])
def review(program_id):
    grade = request.form["grade"]
    comment = request.form["comment"]

    try:
        grade = int(grade)
    except ValueError:
        flash("Virhe: vääränlainen arvosana")
        return redirect(f"/p/{program_id}")

    if grade < 1 or grade > 5:
        flash("Virhe: vääränlainen arvosana")
        return redirect(f"/p/{program_id}")

    try:
        db.execute("INSERT INTO reviews (author, program, grade, comment) VALUES (?, ?, ?, ?)", [session["user_id"], program_id, grade, comment])
    except sqlite3.IntegrityError:
        pass

    return redirect(f"/p/{program_id}")

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)
