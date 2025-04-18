import secrets
import sqlite3

import markupsafe
from flask import Flask, abort, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import Database

app = Flask(__name__)
app.secret_key = "2d0428696ca1cfc52c25ab54228c171f"
db = Database("database.db")

@app.route("/")
def index():
    # TODO: pagination
    programs = db.query("SELECT p.id, p.name, p.description, u.username, u.id, IFNULL(AVG(r.grade), 0) FROM programs p, users u LEFT JOIN reviews r ON r.program = p.id WHERE u.id = p.author GROUP BY p.id ORDER BY p.id DESC")
    programs = [{"id": p[0], "name": p[1], "description": p[2], "author_name": p[3], "author_id": p[4], "grade": p[5]} for p in programs]

    return render_template("index.html", programs=programs)

@app.route("/search")
def search():
    if "text" not in request.args:
        return redirect("/")

    searchtext = request.args["text"]

    # TODO: pagination
    programs = db.query("SELECT p.id, p.name, p.description, u.username, u.id, IFNULL(AVG(r.grade), 0) FROM programs p, users u LEFT JOIN reviews r ON r.program = p.id WHERE u.id = p.author AND (p.name LIKE ? OR p.description LIKE ?) GROUP BY p.id ORDER BY p.id DESC", ["%" + searchtext + "%", "%" + searchtext + "%"])
    programs = [{"id": p[0], "name": p[1], "description": p[2], "author_name": p[3], "author_id": p[4], "grade": p[5]} for p in programs]

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
        session["csrf_token"] = secrets.token_hex(16)
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
    check_csrf()

    del session["username"]
    del session["user_id"]
    flash("Kirjauduttu ulos")
    return redirect("/")

@app.route("/create")
def create_page():
    res = db.query("SELECT c.name, v.value, v.id, c.id FROM classes c, class_value v WHERE v.class = c.id ORDER BY c.name, v.value")

    classes = {}
    for class_value in res:
        # (class_name, class_id)
        id = (class_value[0], class_value[3])

        if id not in classes:
            classes[id] = []

        classes[id].append((class_value[1], class_value[2]))

    classes = [{"name": x[0][0], "id": x[0][1], "options": x[1]} for x in classes.items()]

    return render_template("create.html", classes=classes)

@app.route("/create", methods=["POST"])
def create():
    check_csrf()
    
    if "username" not in session:
        return redirect("/", code=403)

    name = request.form["name"]
    source_link = request.form["source_link"]
    download_link = request.form["download_link"]
    description = request.form["description"]

    all_classes = db.query("SELECT c.id FROM classes c")

    values = []
    for (clas,) in all_classes:
        values.append(request.form[f"class{clas}"])

    program_id = db.execute("INSERT INTO programs (author, name, source_link, download_link, description) VALUES (?, ?, ?, ?, ?)", [session["user_id"], name, source_link, download_link, description])

    for value in values:
        db.execute("INSERT INTO program_class_value (program, value) VALUES (?, ?)", [program_id, value])

    return redirect(f"/p/{program_id}")

@app.route("/p/<int:program_id>")
def program_page(program_id):
    try:
        name, author_name, author_id, source_link, download_link, description, grade = db.query("SELECT p.name, u.username, u.id, p.source_link, p.download_link, p.description, IFNULL(AVG(r.grade), 0) FROM programs p, users u LEFT JOIN reviews r ON r.program = p.id WHERE p.author = u.id AND p.id = ?", [program_id])[0]
    except IndexError:
        flash("Sovellusta ei löytynyt")
        return redirect("/", 404)

    reviews = db.query("SELECT r.grade, r.comment, u.username, u.id FROM users u, programs p LEFT JOIN reviews r ON r.program = p.id WHERE u.id = r.author AND p.id = ?", [program_id])
    reviews = [{"grade": r[0], "comment": r[1], "username": r[2], "user_id": r[3]} for r in reviews]

    can_review = "user_id" in session

    classes = db.query("SELECT c.name, cv.value FROM program_class_value pcv, class_value cv, classes c WHERE pcv.program = ? AND pcv.value = cv.id AND c.id = cv.class ORDER BY c.name, cv.value", [program_id])

    return render_template("program.html", name=name, author_name=author_name, author_id=author_id, source_link=source_link, download_link=download_link, description=description, program_id=program_id, can_review=can_review, reviews=reviews, grade=grade, classes=classes)

@app.route("/p/<int:program_id>/edit")
def program_edit_page(program_id):
    try:
        name, source_link, download_link, description, program_id = db.query("SELECT p.name, p.source_link, p.download_link, p.description, p.id FROM programs p, users u WHERE p.author = u.id AND p.id = ?", [program_id])[0]
    except IndexError:
        flash("Sovellusta ei löytynyt")
        return redirect("/", 404)

    return render_template("edit.html", name=name, source_link=source_link, download_link=download_link, description=description, program_id=program_id)

@app.route("/p/<int:program_id>/edit", methods=["POST"])
def program_edit(program_id):
    check_csrf()
    
    if "username" not in session:
        return redirect("/", code=403)

    name = request.form["name"]
    source_link = request.form["source_link"]
    download_link = request.form["download_link"]
    description = request.form["description"]

    db.execute("UPDATE programs SET name = ?, source_link = ?, download_link = ?, description = ? WHERE id = ? AND author = ?", [name, source_link, download_link, description, program_id, session["user_id"]])

    return redirect(f"/p/{program_id}")

@app.route("/p/<int:program_id>/delete", methods=["POST"])
def delete_program(program_id):
    check_csrf()

    if "user_id" not in session:
        return redirect("/", 404)

    db.execute("DELETE FROM programs WHERE id = ? AND author = ?", [program_id, session["user_id"]])
    db.execute("DELETE FROM program_class_value WHERE program = ?", [program_id])

    return redirect ("/")

@app.route("/p/<int:program_id>/review", methods=["POST"])
def review(program_id):
    check_csrf()

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
        flash("Virhe: olet jo lisännyt arvostelun")

    return redirect(f"/p/{program_id}")

@app.route("/u/<int:user_id>")
def user_page(user_id):
    try:
        average_given_review, review_count = db.query("SELECT IFNULL(AVG(r.grade), 0), COUNT(r.id) FROM users u LEFT JOIN reviews r ON r.author = u.id WHERE u.id = ?", [user_id])[0]

        data = db.query("SELECT u.id, u.username, p.id, p.name, p.description, IFNULL(AVG(r.grade), 0) FROM users u LEFT JOIN programs p ON p.author = u.id LEFT JOIN reviews r ON r.program = p.id WHERE u.id = ? GROUP BY p.id ORDER BY p.id ASC", [user_id])

        user_id = data[0][0]
        name = data[0][1]
    except IndexError:
        flash("Käyttäjää ei löytynyt")
        return redirect("/", 404)

    programs = [{"name": d[3], "description": d[4], "grade": d[5], "id": d[2], "author_name": name, "author_id": user_id} for d in data]
    average_grade = sum([program["grade"] for program in programs])/len(programs)

    return render_template("user.html", name=name, programs=programs, average_given_review=average_given_review, review_count=review_count, average_grade=average_grade)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\r", "")

    while "\n\n" in content:
        content = content.replace("\n\n", "\n")

    content = content.replace("\n", "</p><p>")
    content = "<p>" + content + "</p>"
    return markupsafe.Markup(content)

def check_csrf():
    if "csrf_token" not in session or request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
