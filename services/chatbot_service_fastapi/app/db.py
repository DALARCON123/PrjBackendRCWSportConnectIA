import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------------
# Charger les variables d'environnement depuis le fichier .env
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# -------------------------------------------------------
# URL de la base de données PostgreSQL
# -------------------------------------------------------
DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/sportconnect")

# -------------------------------------------------------
# Création du moteur SQLAlchemy
# -------------------------------------------------------
engine = create_engine(DB_URL)

# -------------------------------------------------------
# Session utilisée pour interagir avec la base de données
# -------------------------------------------------------
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
