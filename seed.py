import random
import sqlite3
import sys

conn = sqlite3.connect("database.db")

with open("schema.sql", "r", encoding="utf-8") as f:
    schema = f.read()

try:
    conn.executescript(schema)
except sqlite3.OperationalError:
    pass

with open("init.sql", "r", encoding="utf-8") as f:
    initscript = f.read()

conn.executescript(initscript)

ADJ = ["hieno", "mahtava", "paras", "nopea", "nopein", "pimeä", "kulmikas",
       "kuninkaallinen", "hieman hidas mutta melkein nopea", "turha",
       "hyödyllinen", "linuxilla toimiva", "epäjärjestelmällinen",
       "järestelmällistyttävä", "virtuaalinen", "terminaalissa toimiva",
       "punainen", "olemassaoleva"]
NOUN = ["ohjelma", "tiedonlaskin", "verkkosivu", "laskin", "peli",
    "terminaali", "käyttöjärjestelmä", "widgetti", "työpöytä", "tiikeri",
    "tuoli", "verkkoselain", "tietokoneensammuttaja", "turhuus", "nappi",
    "ajuri", "ohjain", "hiiri", "editori", "tekstieditori", "näytönsulkija",
    "tuulilasinpyyhkijä"]

USER_COUNT = 10000
MAX_PROGRAMS_PER_USER = 500
MAX_REVIEWS_PER_USER = 1000

print("Seedaus kannattaa ajaa vain, jos tietokanta on tyhjä.", end=" ")
res = input("Haluatko ajaa seedauksen? (E/k) ")

if res.lower() != "k":
    print("Peruttu")
    sys.exit(0)

print("Luodaan käyttäjät...")

users = []

for i in range(USER_COUNT):
    username = "käyttäjä" + str(i + 1)
    password = "********"
    sql = "INSERT INTO users (username, password) VALUES (?, ?)"

    res = conn.execute(sql, [username, password])
    users.append(res.lastrowid)

print("Luodaan ohjelmat...")

# get all classes
sql = """SELECT c.name, v.value, v.id, c.id FROM classes c, class_value v
         WHERE v.class = c.id ORDER BY c.name, v.value"""
res = conn.execute(sql)

classes = {}
for class_value in res:
    # (class_name, class_id)
    key = (class_value[0], class_value[3])

    if key not in classes:
        classes[key] = []

    classes[key].append((class_value[1], class_value[2]))

classes = [(clas[0][0], clas[0][1], clas[1])
           for clas in classes.items()]

programs = []

for user_id in users:
    for i in range(random.randint(1, MAX_PROGRAMS_PER_USER)):
        name = f"{random.choice(ADJ)} {random.choice(NOUN)} {user_id}-{i}"
        url = "https://example.com/" + name.replace(" ", "-")
        description = "ehkä paras projektini ikinä.\n\n"
        description += "tein sellasen ohjelman joka vähän tekee niitä ja näitä"
        description += ". sen nimi on " + name + ". "
        description += "se tekee hienoja asioita, kannattaa kokeilla."

        values = [random.choice(clas[2])[1] for clas in classes]

        sql = """INSERT INTO programs (author, name, source_link, download_link,
                 description) VALUES (?, ?, ?, ?, ?)"""
        program_id = conn.execute(sql, [user_id, name, url,
                                url, description]).lastrowid

        programs.append(program_id)

        for value in values:
            sql = "INSERT INTO program_class_value (program, value) VALUES (?, ?)"
            conn.execute(sql, [program_id, value])

print("Luodaan arvostelut...")

for user_id in users:
    for i in range(random.randint(1, MAX_REVIEWS_PER_USER)):
        grade = random.randint(1, 5)
        comment = f"ihan {random.choice(ADJ)} ohjelma. vähän vois parantaa."
        program_id = random.choice(programs)

        try:
            sql = """INSERT INTO reviews (author, program, grade, comment)
                     VALUES (?, ?, ?, ?)"""
            conn.execute(sql, [user_id, program_id, grade, comment])
        except sqlite3.IntegrityError:
            # reviewed this program already, just ignore it and move on
            pass

conn.commit()
conn.close()
