import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "sports.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS sports (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          categorie TEXT
        )
        """)
        # seed si está vacío
        cur = c.execute("SELECT COUNT(*) AS n FROM sports").fetchone()
        if cur["n"] == 0:
            c.executemany(
                "INSERT INTO sports(name,categorie) VALUES(?,?)",
                [
                    ("Football", "Équipe"),
                    ("Basketball", "Équipe"),
                    ("Tennis", "Individuel"),
                    ("Natation", "Individuel"),
                    ("Course", "Individuel"),
                    ("Volleyball", "Équipe"),
                ],
            )
