"""
Database configuration for Sports Service
Uses PostgreSQL for user data and objectives
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------------------------------------
# Charger les variables d'environnement depuis le fichier .env
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# -------------------------------------------------------
# URL de connexion PostgreSQL
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
# Base : classe de base pour tous les modèles
# -------------------------------------------------------
Base = declarative_base()


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

