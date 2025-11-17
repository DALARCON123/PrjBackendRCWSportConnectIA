# services/sports_service_fastapi/app/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os

# =========================
#   Cargar .env de la raíz
# =========================
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

SPORTS_PORT = int(os.getenv("SPORTS_PORT") or os.getenv("PORT", "8002"))

app = FastAPI(title="Sports Service")

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

SPORTS = [
    {"id": "run", "name": "Running", "level": "beginner"},
    {"id": "yoga", "name": "Yoga", "level": "all"},
    {"id": "swim", "name": "Natación", "level": "all"},
    {"id": "strength", "name": "Fuerza", "level": "intermediate"},
]


@app.get("/sports")
def list_sports():
    return SPORTS


@app.get("/sports/search")
def search(q: str = Query("")):
    ql = q.lower()
    return [s for s in SPORTS if ql in s["name"].lower()]


# Solo si ejecutas este servicio directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=SPORTS_PORT, reload=True)
