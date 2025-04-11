import sqlite3
import os

class Database:
    def __init__(self, filename: str, reset: bool = False):
        self.filename = filename

        if reset:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

        conn = self._connection()

        f = open("schema.sql", "r")
        schema = f.read()

        try:
            conn.executescript(schema)
        except sqlite3.OperationalError:
            pass

        f = open("init.sql", "r")
        initscript = f.read()

        conn.executescript(initscript)

        conn.close()

    def execute(self, query, params=[]):
        conn = self._connection()

        try:
            result = conn.execute(query, params)
        except Exception as e:
            conn.close()
            raise e

        conn.commit()
        conn.close()
        return result.lastrowid

    def query(self, query, params=[]):
        conn = self._connection()

        try:
            result = conn.execute(query, params).fetchall()
        except Exception as e:
            conn.close()
            raise e

        conn.close()
        return result

    def _connection(self):
        return sqlite3.connect(self.filename)

