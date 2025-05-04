from dataclasses import dataclass
import sqlite3

import config
from db import db

def get_program(program_id):
    try:
        sql = """SELECT p.name, u.username, u.id, p.source_link,
                 p.download_link, p.description, IFNULL(AVG(r.grade), 0)
                 FROM programs p, users u
                 LEFT JOIN reviews r ON r.program = p.id
                 WHERE p.author = u.id AND p.id = ?"""
        res = db.query(sql, [program_id])[0]

        name = res[0]
        author_name = res[1]
        author_id = res[2]
        source_link = res[3]
        download_link = res[4]
        description = res[5]
        grade = res[6]
    except IndexError:
        raise ProgramNotFound

    sql = """SELECT c.name, cv.value
             FROM program_class_value pcv, class_value cv, classes c
             WHERE pcv.program = ? AND pcv.value = cv.id AND c.id = cv.class
             ORDER BY c.name, cv.value"""
    classes = db.query(sql, [program_id])

    return Program(name, program_id, author_name, author_id, description, source_link, download_link, grade, classes)

def get_programs(page=0):
    sql = """SELECT p.id, p.name, p.description, u.username, u.id,
             IFNULL(AVG(r.grade), 0) FROM programs p, users u
             LEFT JOIN reviews r ON r.program = p.id
             WHERE u.id = p.author GROUP BY p.id ORDER BY p.id DESC LIMIT ? OFFSET ?"""
    programs = db.query(sql, [config.ITEMS_PER_PAGE + 1, page * config.ITEMS_PER_PAGE])
    programs = [Program(p[1], p[0], p[3], p[4], p[2], None, None, p[5], None) for p in programs]

    has_more = False

    if len(programs) == config.ITEMS_PER_PAGE + 1:
        programs = programs[:-1]
        has_more = True

    return ProgramListing(programs, has_more)

def search_programs(searchtext, page=0):
    sql = """SELECT p.id, p.name, p.description, u.username, u.id,
             IFNULL(AVG(r.grade), 0) FROM programs p, users u
             LEFT JOIN reviews r ON r.program = p.id
             WHERE u.id = p.author AND (p.name LIKE ? OR p.description LIKE ?)
             GROUP BY p.id ORDER BY p.id DESC LIMIT ? OFFSET ?"""
    programs = db.query(sql, ["%" + searchtext + "%", "%" + searchtext + "%",
                              config.ITEMS_PER_PAGE + 1,
                              page * config.ITEMS_PER_PAGE])
    programs = [Program(p[1], p[0], p[3], p[4], p[2], None, None, p[5], None) for p in programs]

    has_more = False

    if len(programs) == config.ITEMS_PER_PAGE + 1:
        programs = programs[:-1]
        has_more = True

    return ProgramListing(programs, has_more)

def create_program(author_id, name, source_link, download_link, description,
                   class_values):
    sql = """INSERT INTO programs (author, name, source_link, download_link,
             description) VALUES (?, ?, ?, ?, ?)"""
    try:
        program_id = db.execute(sql, [author_id, name, source_link,
                                download_link, description])
    except sqlite3.IntegrityError:
        raise ProgramExists

    for value in class_values:
        sql = "INSERT INTO program_class_value (program, value) VALUES (?, ?)"
        db.execute(sql, [program_id, value])

    return program_id

def update_program(program_id, author_id, name, source_link, download_link, description):
    sql = """UPDATE programs SET name = ?, source_link = ?, download_link = ?,
             description = ? WHERE id = ? AND author = ?"""
    db.execute(sql, [name, source_link, download_link, description, program_id,
                     author_id])

def delete_program(program_id):
    db.execute("DELETE FROM programs WHERE id = ?", [program_id])
    db.execute("DELETE FROM program_class_value WHERE program = ?",
               [program_id])
    db.execute("DELETE FROM reviews WHERE program = ?", [program_id])

def review_program(program_id, author_id, grade, comment):
    try:
        sql = """INSERT INTO reviews (author, program, grade, comment)
                 VALUES (?, ?, ?, ?)"""
        db.execute(sql, [author_id, program_id, grade, comment])
    except sqlite3.IntegrityError:
        raise ReviewedAlready

def get_reviews(program_id):
    sql = """SELECT r.grade, r.comment, u.username, u.id
             FROM users u, programs p LEFT JOIN reviews r ON r.program = p.id
             WHERE u.id = r.author AND p.id = ?"""
    reviews = db.query(sql, [program_id])
    reviews = [Review(r[0], r[1], r[3], r[2]) for r in reviews]

    return reviews

def get_classes():
    sql = """SELECT c.name, v.value, v.id, c.id FROM classes c, class_value v
             WHERE v.class = c.id ORDER BY c.name, v.value"""
    res = db.query(sql)

    classes = {}
    for class_value in res:
        # (class_name, class_id)
        key = (class_value[0], class_value[3])

        if key not in classes:
            classes[key] = []

        classes[key].append(ClassOption(class_value[1], class_value[2]))

    classes = [ProgramClass(clas[0][0], clas[0][1], clas[1])
               for clas in classes.items()]

    return classes

def class_ids():
    classes = db.query("SELECT c.id FROM classes c")
    return [x[0] for x in classes]

@dataclass
class ClassOption:
    name: str
    id: int

@dataclass
class ProgramClass:
    name: str
    id: int
    options: list[ClassOption]

@dataclass
class Program:
    name: str
    id: int
    author_name: str
    author_id: int
    description: str
    source_link: str
    download_link: str
    grade: float
    classes: list[tuple[str, str]]

@dataclass
class ProgramListing:
    programs: list[Program]
    has_more: bool

@dataclass
class Review:
    grade: int
    comment: str
    author_id: int
    author_name: int

class ProgramExists(Exception):
    pass

class ProgramNotFound(Exception):
    pass

class ReviewedAlready(Exception):
    pass
