# services/reco_service_fastapi/app/main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx

from .tracking_db import init_db, get_conn  # tracking SQLite
from .firebase_client import db, fb_firestore  # Firestore (Firebase)

# =========================
#   Cargar .env de la raíz
# =========================
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

RECO_PORT = int(os.getenv("RECO_PORT") or os.getenv("PORT", "8003"))
CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8010/chat/ask").rstrip("/")

# =========================
#   Crear app FastAPI
# =========================
app = FastAPI(title="Reco Service")

# CORS para el frontend Vite
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


# === Inicializar BD SQLite al arrancar ===
@app.on_event("startup")
def bootstrap():
    init_db()


# =========================
#   MODELOS RECO IA
# =========================
class RecoRequest(BaseModel):
    user_id: str
    lang: Optional[str] = None  # si no viene, usamos la del perfil


@app.get("/reco/health")
async def reco_health():
    return {"status": "ok", "service": "reco"}


def build_question_from_profile(profile: Dict[str, Any]) -> str:
    """
    Construye un mensaje para el Coach IA usando los datos del usuario.
    """
    name = profile.get("name", "l'utilisateur")
    age = profile.get("age")
    weight = profile.get("weightKg")
    height = profile.get("heightCm")
    goal = profile.get("mainGoal", "")

    parts = [f"Profil de l'utilisateur {name} :"]

    if age is not None:
        parts.append(f"- Âge : {age} ans")
    if weight is not None:
        parts.append(f"- Poids : {weight} kg")
    if height is not None:
        parts.append(f"- Taille : {height} cm")
    if goal:
        parts.append(f"- Objectif principal : {goal}")

    parts.append(
        "\nEn te basant sur ce profil, propose : "
        "1) un plan d'entraînement hebdomadaire simple, "
        "2) des conseils d'alimentation saine adaptés à l'objectif, "
        "3) un conseil de motivation ou de récupération."
    )

    return "\n".join(parts)


async def call_chatbot(message: str, lang: str) -> str:
    """
    Llama al microservicio de chatbot para obtener la recomendación.
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                CHATBOT_URL,
                json={"message": message, "lang": lang},
            )
            resp.raise_for_status()
            data = resp.json()
            return (data.get("answer") or "").strip()
    except Exception as e:
        print(f"Error llamando al chatbot: {e}")
        return ""


@app.post("/reco/generate")
async def generate_recommendation(req: RecoRequest):
    """
    1) Lee el perfil de usuario en Firestore (colección users)
    2) Construye una pregunta para el Coach IA
    3) Llama al chatbot
    4) Guarda la recomendación en users/{uid}/recommendations
    5) Devuelve la respuesta
    """
    # 1) Leer perfil
    user_ref = db.collection("users").document(req.user_id)
    snap = user_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    profile = snap.to_dict() or {}
    lang = (req.lang or profile.get("lang") or "fr").lower()

    # 2) Pregunta
    question = build_question_from_profile(profile)

    # 3) Chatbot
    answer = await call_chatbot(question, lang)
    if not answer:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la génération de la recommandation",
        )

    # 4) Guardar en subcolección recommendations
    reco_ref = user_ref.collection("recommendations").document()  # ID automático

    reco_data = {
        "question": question,
        "answer": answer,
        "createdAt": fb_firestore.SERVER_TIMESTAMP,
        "age": profile.get("age"),
        "weightKg": profile.get("weightKg"),
        "heightCm": profile.get("heightCm"),
        "mainGoal": profile.get("mainGoal"),
        "lang": lang,
    }

    reco_ref.set(reco_data)

    # 5) Devolver
    return {"answer": answer, "profile": profile}


@app.get("/reco/history/{user_id}")
async def get_history(user_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve el historial de recomendaciones IA del usuario.
    """
    user_ref = db.collection("users").document(user_id)

    docs = (
        user_ref.collection("recommendations")
        .order_by("createdAt", direction=fb_firestore.Query.DESCENDING)
        .stream()
    )

    history: List[Dict[str, Any]] = []
    for d in docs:
        item = d.to_dict()
        item["id"] = d.id
        history.append(item)

    return history


# ------------ MODELOS TRACKING (SQLite) ------------
class MeasurementIn(BaseModel):
    date: str
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    notes: Optional[str] = None


class MeasurementOut(MeasurementIn):
    id: int


# ------------ ENDPOINTS TRACKING (SQLite) ------------
@app.get("/tracking/measurements", response_model=List[MeasurementOut])
def get_measurements(email: str = Query(...)):
    with get_conn() as c:
        cur = c.cursor()
        cur.execute(
            """
            SELECT id, date, weight_kg, waist_cm, hips_cm, chest_cm, notes
            FROM measurements
            WHERE email=?
            ORDER BY date DESC, id DESC
            """,
            (email.lower(),),
        )
        rows = [dict(r) for r in cur.fetchall()]
    return rows


@app.post("/tracking/measurements", response_model=dict)
def add_measurement(email: str, body: MeasurementIn):
    if not body.date:
        raise HTTPException(status_code=400, detail="date is required")

    with get_conn() as c:
        cur = c.cursor()
        cur.execute(
            """
            INSERT INTO measurements(
                email, date, weight_kg, waist_cm, hips_cm, chest_cm, notes
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                email.lower(),
                body.date,
                body.weight_kg,
                body.waist_cm,
                body.hips_cm,
                body.chest_cm,
                body.notes,
            ),
        )
        c.commit()
        new_id = cur.lastrowid

    return {"ok": True, "id": new_id}


# Solo si ejecutas este servicio directamente
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=RECO_PORT, reload=True)
