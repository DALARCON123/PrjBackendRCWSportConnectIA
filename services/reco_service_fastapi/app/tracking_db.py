# services/reco_service_fastapi/app/tracking_db.py
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "tracking.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as c:
        cur = c.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS measurements(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT NOT NULL,
          date TEXT NOT NULL,
          weight_kg REAL,
          waist_cm REAL,
          hips_cm REAL,
          chest_cm REAL,
          notes TEXT
        );
        """
        )
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS recommendations(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id TEXT NOT NULL,
          email TEXT NOT NULL,
          type TEXT NOT NULL,
          content TEXT NOT NULL,
          created_at TEXT NOT NULL,
          metadata TEXT
        );
        """
        )
        # si luego quieres más tablas (workouts, nutrition_logs), agrégalas aquí
        c.commit()
