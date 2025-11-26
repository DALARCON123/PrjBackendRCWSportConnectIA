# services/reco_service_fastapi/app/tracking_db.py

import sqlite3
from contextlib import closing
from pathlib import Path

# -------------------------------------------------------
# Chemin de la base SQLite (tracking.db)
# -------------------------------------------------------
DB_PATH = Path(__file__).resolve().parent.parent / "tracking.db"

# -------------------------------------------------------
# Ouvre une connexion SQLite et active l’accès par nom de colonne
# -------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------------
# Initialise la base : création de la table measurements
# -------------------------------------------------------
def init_db():
    with closing(get_conn()) as c:
        cur = c.cursor()
        cur.execute("""
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
        """)
        # Plus tard : ajouter d’autres tables si nécessaire
        c.commit()
