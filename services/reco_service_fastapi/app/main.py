# services/reco_service_fastapi/app/main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx

from .tracking_db import init_db, get_conn      # SQLite pour le suivi
from .firebase_client import db, fb_firestore   # Firestore (Firebase)

# -------------------------------------------------------
# Charger le fichier .env à la racine du projet
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

RECO_PORT = int(os.getenv("RECO_PORT") or os.getenv("PORT", "8003"))
CHATBOT_URL = os.getenv(
    "CHATBOT_URL",
    "http://localhost:8010/chat/ask"
).rstrip("/")

print(f"[RECO] CHATBOT_URL = {CHATBOT_URL}")

# -------------------------------------------------------
# Création de l’application FastAPI
# -------------------------------------------------------
app = FastAPI(title="Reco Service")

# -------------------------------------------------------
# CORS pour permettre les appels du frontend Vite
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
# Initialiser la base SQLite au démarrage
# -------------------------------------------------------
@app.on_event("startup")
def bootstrap():
    print("[RECO] Initialisation de la base SQLite…")
    init_db()
    print("[RECO] SQLite OK.")

# -------------------------------------------------------
# Modèle d’entrée : demande de recommandation
# -------------------------------------------------------
class RecoRequest(BaseModel):
    user_id: str
    lang: Optional[str] = None

# -------------------------------------------------------
# Route santé du service
# -------------------------------------------------------
@app.get("/reco/health")
async def reco_health():
    return {"status": "ok", "service": "reco"}

# -------------------------------------------------------
# Construire une question selon le profil (Firestore ou défaut)
# -------------------------------------------------------
def build_question_from_profile(profile: Dict[str, Any]) -> str:
    """
    Construit un descriptif du profil + consigne pour le coach IA.
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
        "\nSur ce profil, donne :\n"
        "1) un plan d'entraînement simple (3 à 5 séances par semaine max),\n"
        "2) quelques conseils d’alimentation et d’hydratation,\n"
        "3) un conseil de récupération / sommeil / motivation.\n"
        "Sois concret mais prudent : intensité progressive, échauffement, "
        "étirements légers et recommandation de consulter un professionnel "
        "de la santé en cas de douleur ou de condition médicale."
    )
    return "\n".join(parts)

# -------------------------------------------------------
# Appel au microservice chatbot pour générer la réponse IA
# -------------------------------------------------------
async def call_chatbot(message: str, lang: str) -> str:
    """
    Appelle le service /chat/ask.
    Retourne la réponse texte, ou "" en cas de problème.
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                CHATBOT_URL,
                json={"message": message, "lang": lang},
            )
            resp.raise_for_status()
            data = resp.json()
            answer = (data.get("answer") or "").strip()
            print(f"[RECO] Réponse chatbot (extrait) -> {answer[:80]}...")
            return answer
    except Exception as e:
        print(f"[RECO] Erreur en appelant le chatbot: {e}")
        return ""

# -------------------------------------------------------
# Endpoint principal : générer recommandation IA
# -------------------------------------------------------
@app.post("/reco/generate")
async def generate_recommendation(req: RecoRequest):
    """
    1) Lit (ou crée) un profil utilisateur dans Firestore
    2) Construit une question détaillée pour le Coach IA
    3) Appelle le microservice chatbot
    4) Sauvegarde la recommandation dans Firestore (si possible)
    5) Retourne { answer, profile } au frontend
    """

    # -------- Profil par défaut (mêmes valeurs que dans le frontend) --------
    default_profile: Dict[str, Any] = {
        "name": "SportConnectIA",
        "age": 39,
        "weightKg": 64,
        "heightCm": 160,
        "mainGoal": "Perte de poids",
        "lang": "fr",
    }

    profile: Dict[str, Any] = default_profile.copy()
    firestore_ok = True
    user_ref = None

    # -------- 1) Lire ou créer le profil dans Firestore --------
    try:
        user_ref = db.collection("users").document(req.user_id)
        snap = user_ref.get()

        if snap.exists:
            data = snap.to_dict() or {}
            # on fusionne les données Firestore avec les valeurs par défaut
            profile.update({
                "name": data.get("name") or profile["name"],
                "age": data.get("age", profile["age"]),
                "weightKg": data.get("weightKg", profile["weightKg"]),
                "heightCm": data.get("heightCm", profile["heightCm"]),
                "mainGoal": data.get("mainGoal") or profile["mainGoal"],
                "lang": data.get("lang") or profile["lang"],
            })
        else:
            # si l'utilisateur n'existe pas, on le crée avec le profil par défaut
            print(f"[RECO] Utilisateur {req.user_id} absent → création profil par défaut.")
            user_ref.set(default_profile, merge=True)

    except Exception as e:
        # Si Firestore est down ou mal configuré, on continue quand même
        print(f"[RECO] Erreur Firestore (lecture/écriture profil) : {e}")
        firestore_ok = False

    # langue finale (priorité : requête -> profil -> fr)
    lang = (req.lang or profile.get("lang") or "fr").lower()

    # -------- 2) Construire la question pour le Coach IA --------
    question = build_question_from_profile(profile)
    print(f"[RECO] Question envoyée au chatbot:\n{question}")

    # -------- 3) Appeler le microservice chatbot --------
    answer = await call_chatbot(question, lang)
    if not answer:
        # Ici on renvoie une erreur 500 au frontend
        # (le frontend affiche ton message rouge)
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la réponse IA depuis le chatbot."
        )

    # -------- 4) Sauvegarder l'historique dans Firestore (si possible) --------
    if firestore_ok and user_ref is not None:
        try:
            reco_ref = user_ref.collection("recommendations").document()
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
            print(f"[RECO] Recommandation enregistrée pour user {req.user_id}.")
        except Exception as e:
            # On log l'erreur, mais on n'empêche pas la réponse au frontend
            print(f"[RECO] Erreur Firestore en sauvegardant l'historique: {e}")

    # -------- 5) Retourner la recommandation + le profil --------
    return {"answer": answer, "profile": profile}

# -------------------------------------------------------
# Obtenir l’historique des recommandations IA
# -------------------------------------------------------
@app.get("/reco/history/{user_id}")
async def get_history(user_id: str) -> List[Dict[str, Any]]:
    """
    Retourne la liste des recommandations passées d'un utilisateur,
    triées de la plus récente à la plus ancienne.
    Si Firestore pose problème, on renvoie simplement une liste vide.
    """
    history: List[Dict[str, Any]] = []

    try:
        user_ref = db.collection("users").document(user_id)
        docs = (
            user_ref.collection("recommendations")
            .order_by("createdAt", direction=fb_firestore.Query.DESCENDING)
            .stream()
        )

        for d in docs:
            item = d.to_dict() or {}
            item["id"] = d.id
            history.append(item)

    except Exception as e:
        print(f"[RECO] Erreur Firestore get_history pour user {user_id}: {e}")
        # on retourne quand même une liste vide pour éviter un 500

    return history

# -------------------------------------------------------
# Modèles pour mesures corporelles (SQLite)
# -------------------------------------------------------
class MeasurementIn(BaseModel):
    date: str
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    notes: Optional[str] = None

class MeasurementOut(MeasurementIn):
    id: int

# -------------------------------------------------------
# Obtenir toutes les mesures pour un utilisateur
# -------------------------------------------------------
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

# -------------------------------------------------------
# Ajouter une nouvelle mesure
# -------------------------------------------------------
@app.post("/tracking/measurements", response_model=dict)
def add_measurement(email: str, body: MeasurementIn):
    if not body.date:
        raise HTTPException(400, "date is required")

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

# -------------------------------------------------------
# Exécuter le service directement (mode local)
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=RECO_PORT, reload=True)
