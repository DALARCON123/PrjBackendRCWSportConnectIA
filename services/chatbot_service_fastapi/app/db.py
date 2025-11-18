import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------------
# URL de la base de données (par défaut SQLite "coach.db")
# -------------------------------------------------------
DB_URL = os.getenv("DB_URL", "sqlite:///./coach.db")

# -------------------------------------------------------
# Création du moteur SQLAlchemy
# check_same_thread=False : nécessaire pour SQLite + FastAPI
# -------------------------------------------------------
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
)

# -------------------------------------------------------
# Session utilisée pour interagir avec la base de données
# -------------------------------------------------------
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
