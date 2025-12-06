# services/reco_service_fastapi/app/main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx

from .mongodb_client import (
    users_collection,
    recommendations_collection,
    health_metrics_collection,  
) # MongoDB pour les métriques

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
# Pas besoin d'initialiser SQLite, on utilise MongoDB
# -------------------------------------------------------
@app.on_event("startup")
def bootstrap():
    print("[RECO] Service démarré. Utilisation de MongoDB pour le tracking.")
    print("[RECO] Collections: users, recommendations, health_metrics")

# -------------------------------------------------------
# Modèle d’entrée : demande de recommandation
# -------------------------------------------------------
class RecoRequest(BaseModel):
    user_id: str
    lang: Optional[str] = None

# -------------------------------------------------------
# Modèle d’entrée : demande de recommandation
# -------------------------------------------------------
class RecoRequest(BaseModel):
    user_id: str
    lang: Optional[str] = None

# <<< NOVO: modèle + endpoint pour /reco/send-report >>>
class SendReportRequest(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    lang: Optional[str] = "fr"


@app.post("/reco/send-report")
async def send_report(req: SendReportRequest):
    """
    Récupère la dernière recommandation de l'utilisateur dans MongoDB
    et retourne un stub de réponse pour l'envoi de rapport.

    (Ici tu peux plus tard brancher ton envoi réel d'e-mail.)
    """
    # 1) Chercher la dernière reco pour cet utilisateur
    try:
        last_reco = recommendations_collection.find_one(
            {"user_id": req.user_id},
            sort=[("createdAt", -1)]
        )
    except Exception as e:
        print(f"[RECO] Erreur MongoDB send_report pour user {req.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur lors de la lecture des recommandations."
        )

    if not last_reco:
        raise HTTPException(
            status_code=404,
            detail="Aucune recommandation trouvée pour cet utilisateur."
        )

    # Ici tu pourrais construire le contenu d'e-mail à partir de last_reco["answer"]
    # et appeler une fonction send_email_smtp(req.email, sujet, contenu)

    print(
        f"[RECO] (stub) Rapport généré pour {req.email} "
        f"avec reco_id={last_reco.get('_id')}"
    )

    return {
        "ok": True,
        "message": "Rapport généré (envoi e-mail à implémenter).",
        "email": req.email,
    }
# <<< FIM DA PARTE NOVA >>>



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
    Construit un descriptif du profil + consignes pour le coach IA.
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
        "\nSur ce profil, produis une réponse en **Markdown** avec "
        "EXACTEMENT 4 sections, dans cet ordre, et rien d'autre :\n\n"
        "1) **Plan**\n"
        "* Résume en 1 à 2 phrases le type de programme adapté.\n\n"
        "2) **Plan d'entraînement (3 séances par semaine max)**\n"
        "* Donne un exemple de programme pour la semaine, sous forme de liste à puces.\n\n"
        "3) **Conseils d'alimentation et d’hydratation**\n"
        "* Liste quelques conseils pratiques (liste à puces).\n\n"
        "4) **Conseil de récupération/sommeil/motivation**\n"
        "* Donne quelques conseils de récupération, sommeil et motivation (liste à puces).\n\n"
        "Chaque section doit commencer par son titre en gras (par ex. `**Plan**`) "
        "sur une ligne seule, suivi d'une liste d'éléments commençant par `* `. "
        "N’ajoute pas d’introduction, pas de conclusion, pas d’emojis en début de ligne."
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

    # -------- 1) Lire ou créer le profil dans MongoDB --------
    try:
        user_doc = users_collection.find_one({"_id": req.user_id})

        if user_doc:
            # on fusionne les données MongoDB avec les valeurs par défaut
            profile.update({
                "name": user_doc.get("name") or profile["name"],
                "age": user_doc.get("age", profile["age"]),
                "weightKg": user_doc.get("weightKg", profile["weightKg"]),
                "heightCm": user_doc.get("heightCm", profile["heightCm"]),
                "mainGoal": user_doc.get("mainGoal") or profile["mainGoal"],
                "lang": user_doc.get("lang") or profile["lang"],
            })
        else:
            # si l'utilisateur n'existe pas, on le crée avec le profil par défaut
            print(f"[RECO] Utilisateur {req.user_id} absent → création profil par défaut.")
            users_collection.insert_one({
                "_id": req.user_id,
                **default_profile
            })

    except Exception as e:
        # Si MongoDB est down ou mal configuré, on continue quand même
        print(f"[RECO] Erreur MongoDB (lecture/écriture profil) : {e}")
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

    # -------- 4) Sauvegarder l'historique dans MongoDB (si possible) --------
    if firestore_ok and user_ref is not None:
        try:
            from datetime import datetime
            reco_data = {
                "user_id": req.user_id,
                "question": question,
                "answer": answer,
                "createdAt": datetime.utcnow(),
                "age": profile.get("age"),
                "weightKg": profile.get("weightKg"),
                "heightCm": profile.get("heightCm"),
                "mainGoal": profile.get("mainGoal"),
                "lang": lang,
            }
            recommendations_collection.insert_one(reco_data)
            print(f"[RECO] Recommandation enregistrée pour user {req.user_id}.")
        except Exception as e:
            # On log l'erreur, mais on n'empêche pas la réponse au frontend
            print(f"[RECO] Erreur MongoDB en sauvegardant l'historique: {e}")

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
    Si MongoDB pose problème, on renvoie simplement une liste vide.
    """
    history: List[Dict[str, Any]] = []

    try:
        docs = recommendations_collection.find(
            {"user_id": user_id}
        ).sort("createdAt", -1)

        for doc in docs:
            # Convertir ObjectId pour JSON
            doc["id"] = str(doc.pop("_id"))
            # Convertir datetime para ISO string
            if "createdAt" in doc:
                doc["createdAt"] = doc["createdAt"].isoformat()
            history.append(doc)

    except Exception as e:
        print(f"[RECO] Erreur MongoDB get_history pour user {user_id}: {e}")
        # on retourne quand même une liste vide pour éviter un 500

    return history

# -------------------------------------------------------
# Modèles pour mesures corporelles (MongoDB)
# -------------------------------------------------------
class MeasurementIn(BaseModel):
    date: str
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    notes: Optional[str] = None

class MeasurementOut(BaseModel):
    id: str
    email: str
    date: str
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    notes: Optional[str] = None

# -------------------------------------------------------
# Obtenir toutes les mesures pour un utilisateur
# -------------------------------------------------------
@app.get("/tracking/measurements", response_model=List[MeasurementOut])
def get_measurements(email: str = Query(...)):
    """
    Retourne toutes les mesures corporelles d'un utilisateur depuis MongoDB
    """
    try:
        measurements = health_metrics_collection.find(
            {"email": email.lower()}
        ).sort("date", -1)
        
        result = []
        for doc in measurements:
            doc["id"] = str(doc.pop("_id"))
            result.append(doc)
        
        return result
    except Exception as e:
        print(f"[RECO] Erreur lors de la récupération des mesures: {e}")
        raise HTTPException(500, f"Erreur serveur: {e}")

# -------------------------------------------------------
# Ajouter une nouvelle mesure
# -------------------------------------------------------
@app.post("/tracking/measurements", response_model=dict)
def add_measurement(email: str, body: MeasurementIn):
    """
    Ajoute une nouvelle mesure corporelle dans MongoDB
    """
    if not body.date:
        raise HTTPException(400, "date is required")

    try:
        measurement_data = {
            "email": email.lower(),
            "date": body.date,
            "weight_kg": body.weight_kg,
            "waist_cm": body.waist_cm,
            "hips_cm": body.hips_cm,
            "chest_cm": body.chest_cm,
            "notes": body.notes or ""
        }
        
        result = health_metrics_collection.insert_one(measurement_data)
        new_id = str(result.inserted_id)
        
        return {"ok": True, "id": new_id}
    except Exception as e:
        print(f"[RECO] Erreur lors de l'ajout de la mesure: {e}")
        raise HTTPException(500, f"Erreur serveur: {e}")

# -------------------------------------------------------
# Exécuter le service directement (mode local)
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=RECO_PORT, reload=True)
