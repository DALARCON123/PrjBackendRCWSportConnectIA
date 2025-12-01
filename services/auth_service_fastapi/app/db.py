# app/db.py
# -------------------------------------------------------
# Configuration de la base de données avec SQLAlchemy
# -------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from dotenv import load_dotenv
import os

# -------------------------------------------------------
# Charger les variables d'environnement depuis le fichier .env
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# -------------------------------------------------------
# URL de connexion PostgreSQL (pour les données des utilisateurs)
# -------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/sportconnect")

# -------------------------------------------------------
# Création du moteur SQLAlchemy
# -------------------------------------------------------
engine = create_engine(DATABASE_URL)

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
