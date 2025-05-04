import secrets
from functools import wraps

import markupsafe
from flask import Flask, abort, flash, redirect, render_template, request, session

import config
from program import (
    ProgramExists,
    ProgramNotFound,
    ReviewedAlready,
    class_ids,
    create_program,
    delete_program,
    get_classes,
    get_program,
    get_programs,
    get_reviews,
    review_program,
    search_programs,
    update_program,
)
from user import (
    UserExists,
    UserNotFound,
    WrongCredentials,
    create_user,
    login,
    user_programs,
    user_stats,
)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def csrf_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ("csrf_token" not in session
            or request.form["csrf_token"] != session["csrf_token"]):
            abort(403)

        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function

# Returns the zero-indexed page number from query parameters showing to the
# user as one-indexed
def get_page():
    page = request.args.get("p", default=1)

    try:
        # zero-indexed
        page = int(page) - 1
    except ValueError:
        page = 0

    return page

@app.route("/")
def index():
    page = get_page()

    listing = get_programs(page=page)

    prev_page = page if page > 0 else None
    next_page = page + 2 if listing.has_more else None

    return render_template("index.html", programs=listing.programs,
                           next_page=next_page, prev_page=prev_page)

@app.route("/search")
def search():
    if "text" not in request.args:
        return redirect("/")

    page = get_page()
    searchtext = request.args["text"]

    listing = search_programs(searchtext, page=page)

    prev_page = page if page > 0 else None
    next_page = page + 2 if listing.has_more else None


    return render_template("search.html", programs=listing.programs,
                           prev_page=prev_page, next_page=next_page,
                           searchtext=searchtext)

@app.route("/login")
def login_page():
    return render_template("login.html", username="")

@app.route("/login", methods=["POST"])
def login_form():
    username = request.form["username"]
    password = request.form["password"]

    try:
        user_id = login(username, password)
    except WrongCredentials:
        flash("Virhe: väärä tunnus tai salasana")
        return render_template("login.html", username=username)

    session["username"] = username
    session["user_id"] = user_id
    session["csrf_token"] = secrets.token_hex(16)
    return redirect("/")

@app.route("/register")
def register_page():
    return render_template("register.html", username="")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        flash("Virhe: salasanat eivät ole samat")
        return render_template("register.html", username=username)

    if (len(password1) < 6 or not username or len(username) > 25
        or len(password1) > 128):
        abort(400)

    try:
        create_user(username, password1)
    except UserExists:
        flash("Virhe: tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu")
    return redirect("/login")

@app.route("/logout", methods=["POST"])
@csrf_required
@login_required
def logout():
    del session["username"]
    del session["user_id"]
    flash("Kirjauduttu ulos")
    return redirect("/")

@app.route("/create")
@login_required
def create_page():
    classes = get_classes()

    return render_template("create.html", classes=classes)

@app.route("/create", methods=["POST"])
@csrf_required
@login_required
def create():
    name = request.form["name"]
    source_link = request.form["source_link"]
    download_link = request.form["download_link"]
    description = request.form["description"]

    if (not (source_link.startswith("http://")
             or source_link.startswith("https://"))
        or not (download_link.startswith("http://")
                or download_link.startswith("https://"))):
        flash("Virhe: virheellinen linkki")
        return redirect("/create")

    if (not name or not source_link or not download_link or not description
        or len(name) > 50 or len(source_link) > 240 or len(download_link) > 240
        or len(description) > 5000):
        abort(400)

    all_classes = class_ids()

    values = []
    for clas in all_classes:
        values.append(request.form[f"class{clas}"])

    try:
        program_id = create_program(session["user_id"], name, source_link,
                                    download_link, description, values)
    except ProgramExists:
        flash("Virhe: samalla nimellä on jo olemassa sovellus")
        return render_template("create.html")

    return redirect(f"/p/{program_id}")

@app.route("/p/<int:program_id>")
def program_page(program_id):
    try:
        program = get_program(program_id)
    except ProgramNotFound:
        flash("Sovellusta ei löytynyt")
        abort(404)

    reviews = get_reviews(program_id)
    can_review = "user_id" in session

    return render_template("program.html", program=program,
                           can_review=can_review, reviews=reviews)

@app.route("/p/<int:program_id>/edit")
@login_required
def program_edit_page(program_id):
    try:
        program = get_program(program_id)
    except IndexError:
        flash("Sovellusta ei löytynyt")
        return redirect("/", 404)

    if session["user_id"] != program.author_id:
        abort(403)

    return render_template("edit.html", program=program)

@app.route("/p/<int:program_id>/edit", methods=["POST"])
@csrf_required
@login_required
def program_edit(program_id):
    name = request.form["name"]
    source_link = request.form["source_link"]
    download_link = request.form["download_link"]
    description = request.form["description"]

    if (not (source_link.startswith("http://")
             or source_link.startswith("https://"))
        or not (download_link.startswith("http://")
                or download_link.startswith("https://"))):
        flash("Virhe: virheellinen linkki")
        return redirect(f"/p/{program_id}/edit")

    if (not name or not source_link or not download_link or not description
        or len(name) > 50 or len(source_link) > 240 or len(download_link) > 240
        or len(description) > 5000):
        abort(400)

    update_program(program_id, session["user_id"], name, source_link, download_link, description)

    return redirect(f"/p/{program_id}")

@app.route("/p/<int:program_id>/delete", methods=["POST"])
@csrf_required
@login_required
def delete_program_form(program_id):
    try:
        program = get_program(program_id)
    except ProgramNotFound:
        abort(404)

    if program.author_id != session["user_id"]:
        abort(403)

    delete_program(program_id)

    return redirect("/")

@app.route("/p/<int:program_id>/review", methods=["POST"])
@csrf_required
@login_required
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

    if not comment or len(comment) > 2000:
        abort(400)

    try:
        review_program(program_id, session["user_id"], grade, comment)
    except ReviewedAlready:
        flash("Virhe: olet jo lisännyt arvostelun")

    return redirect(f"/p/{program_id}")

@app.route("/u/<int:user_id>")
def user_page(user_id):
    page = get_page()

    try:
        stats = user_stats(user_id)
        programs = user_programs(user_id, page=page)
    except UserNotFound:
        abort(404)

    prev_page = page if page > 0 else None
    next_page = page + 2 if programs.has_more else None

    return render_template("user.html", name=stats.name, stats=stats,
                           programs=programs.programs, next_page=next_page,
                           prev_page=prev_page, user_id=user_id)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\r", "")

    while "\n\n" in content:
        content = content.replace("\n\n", "\n")

    content = content.replace("\n", "</p><p>")
    content = "<p>" + content + "</p>"
    return markupsafe.Markup(content)

@app.template_filter("roundf")
def roundf_filter(content, digits):
    return round(float(content), ndigits=digits)
