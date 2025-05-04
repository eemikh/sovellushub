import sqlite3
import os

import config

class Database:
    def __init__(self, filename: str, reset: bool = False):
        self.filename = filename

        if reset:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

        conn = self._connection()

        with open("schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()

        try:
            conn.executescript(schema)
        except sqlite3.OperationalError:
            pass

        with open("init.sql", "r", encoding="utf-8") as f:
            initscript = f.read()

        conn.executescript(initscript)

        conn.close()

    def execute(self, query, params=None):
        # PEP 8 recommended style
        if params is None:
            params = []

        conn = self._connection()

        try:
            result = conn.execute(query, params)
        except Exception as e:
            conn.close()
            raise e

        conn.commit()
        conn.close()
        return result.lastrowid

    def query(self, query, params=None):
        # PEP 8 recommended style
        if params is None:
            params = []

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

db = Database(config.DATABASE_FILE, reset=config.RESET_DB)
