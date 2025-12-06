# services/sports_service_fastapi/app/main.py

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import os

from .db import engine, Base, get_db

# -------------------------------------------------------
# Charger le fichier .env depuis la racine du projet
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# -------------------------------------------------------
# Port du service Sports (défini dans .env)
# -------------------------------------------------------
SPORTS_PORT = int(os.getenv("SPORTS_PORT") or os.getenv("PORT", "8002"))

# -------------------------------------------------------
# Lifespan: initialiser la base de données au démarrage
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[SPORTS] Initialisation de la base PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("[SPORTS] PostgreSQL OK.")
    yield
    # Shutdown (si nécessaire)
    print("[SPORTS] Arrêt du service...")

# -------------------------------------------------------
# Création de l'application FastAPI
# -------------------------------------------------------
app = FastAPI(title="Sports Service", lifespan=lifespan)

# -------------------------------------------------------
# CORS : autoriser les appels du frontend Vite
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Petite base statique de sports disponibles
# -------------------------------------------------------
SPORTS = [
    {"id": "run", "name": "Running", "level": "beginner"},
    {"id": "yoga", "name": "Yoga", "level": "all"},
    {"id": "swim", "name": "Natación", "level": "all"},
    {"id": "strength", "name": "Fuerza", "level": "intermediate"},
]

# -------------------------------------------------------
# Retourne la liste complète des sports
# -------------------------------------------------------
@app.get("/sports")
def list_sports():
    return SPORTS

# -------------------------------------------------------
# Recherche simple par nom (filtre sur la liste)
# -------------------------------------------------------
@app.get("/sports/search")
def search(q: str = Query("")):
    ql = q.lower()
    return [s for s in SPORTS if ql in s["name"].lower()]

# -------------------------------------------------------
# Lancer le service directement depuis Python
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=SPORTS_PORT, reload=True)
