# app/db.py
# -------------------------------------------------------
# Configuration de la base de données avec SQLAlchemy
# -------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

# -------------------------------------------------------
# Dossier courant (app) et chemin du fichier SQLite
# Exemple : services/auth_service_fastapi/app/auth.db
# -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "auth.db"

# URL de connexion SQLite (fichier local)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# -------------------------------------------------------
# Création du moteur SQLAlchemy
# check_same_thread=False : nécessaire avec SQLite + FastAPI
# -------------------------------------------------------
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# -------------------------------------------------------
# SessionLocal : fabrique de sessions pour interagir avec la BD
# -------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------
# Base : classe de base pour tous les modèles (User, Notification, etc.)
# C'est cet objet que tu importes dans models.py
# -------------------------------------------------------
Base = declarative_base()


# -------------------------------------------------------
# Dépendance FastAPI : obtenir une session de BD par requête
# -------------------------------------------------------
def get_db():
    """
    Ouvre une session de base de données pour la requête,
    puis la ferme automatiquement après.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
