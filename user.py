from dataclasses import dataclass
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from db import db
import config
from program import Program

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (?, ?)"

    try:
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        raise UserExists

# Returns the user ID of the user if log in successful, otherwise raises
# WrongCredentials
def login(username, password) -> int:
    sql = "SELECT id, password FROM users WHERE username = ?"
    queryres = db.query(sql, [username])

    if len(queryres) == 0:
        raise WrongCredentials

    user_id, password_hash = queryres[0]

    if not check_password_hash(password_hash, password):
        raise WrongCredentials

    return user_id

def user_stats(user_id):
    try:
        sql = """SELECT u.username, IFNULL(AVG(r.grade), 0), COUNT(r.id) FROM users u
                 LEFT JOIN reviews r ON r.author = u.id WHERE u.id = ?"""
        name, average_given_review, review_count = db.query(sql, [user_id])[0]

        sql = """SELECT IFNULL(AVG(IFNULL(r.grade, 0)), 0), COUNT(DISTINCT p.id)
                 FROM users u
                 LEFT JOIN programs p ON p.author = u.id
                 LEFT JOIN reviews r ON r.program = p.id
                 WHERE u.id = ?"""
        average_grade, program_count = db.query(sql, [user_id])[0]
    except IndexError:
        raise UserNotFound

    return UserStats(name, program_count, average_grade, average_given_review,
                     review_count)

def user_programs(user_id, page=0):
    try:
        sql = """SELECT u.id, u.username, p.id, p.name, p.description,
                 IFNULL(AVG(r.grade), 0) FROM users u
                 LEFT JOIN programs p ON p.author = u.id
                 LEFT JOIN reviews r ON r.program = p.id
                 WHERE u.id = ? GROUP BY p.id ORDER BY p.id ASC
                 LIMIT ? OFFSET ?"""
        data = db.query(sql, [user_id, config.ITEMS_PER_PAGE + 1,
                              config.ITEMS_PER_PAGE * page])

        user_id = data[0][0]
        name = data[0][1]
    except IndexError:
        raise UserNotFound

    # PEP 8 recommended style
    if data[0][2] is None:
        programs = []
    else:
        programs = [Program(d[3], d[2], name, user_id, d[4], None, None, d[5], None) for d in data]

    has_more = False

    if len(programs) == config.ITEMS_PER_PAGE + 1:
        programs = programs[:-1]
        has_more = True

    return UserPrograms(programs, has_more)

@dataclass
class UserStats:
    name: str
    program_count: int
    average_grade: float
    average_given_review: float
    review_count: int

@dataclass
class UserPrograms:
    programs: list[Program]
    has_more: bool

class UserExists(Exception):
    pass

class WrongCredentials(Exception):
    pass

class UserNotFound(Exception):
    pass
