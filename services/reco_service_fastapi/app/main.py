# services/reco_service_fastapi/app/main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx
import smtplib
from email.mime.text import MIMEText
from datetime import datetime 

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

# ------------ SMTP POUR ENVOYER LES EMAILS ------------
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "")


def send_email_smtp(to_email: str, subject: str, html_body: str):
    """
    Envoie un e-mail HTML simple via SMTP (par ex. Gmail).
    """
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        raise RuntimeError("Configuration SMTP incomplète (voir .env).")

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


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

# -------------------------------------------------------
# Modèle d’entrée : demande de recommandation
# -------------------------------------------------------
class RecoRequest(BaseModel):
    user_id: str
    lang: Optional[str] = None



# -------------------------------------------------------
# Fonction pour filtrer le plan d'entraînement selon le jour
# -------------------------------------------------------
def filter_reco_for_today(answer: str, lang: str) -> str:
    """
    Filtre uniquement les lignes de jour de la semaine dans la section
    'Plan d'entraînement / Plan de entrenamiento / Training plan'
    pour garder seulement la séance du jour dans l'e-mail.

    Les autres sections (Plan, alimentation, récupération) restent inchangées.
    """
    if not answer:
        return answer

    # 0 = lundi, 6 = dimanche
    today_idx = datetime.now().weekday()
    lang = (lang or "").lower()

    # Préfixes des bullets à garder pour chaque langue
    if lang.startswith("fr"):
        day_prefixes = {
            0: ["* Lundi"],        # lundi
            2: ["* Mercredi"],     # mercredi
            4: ["* Vendredi"],     # vendredi
            5: ["* Option"],       # samedi → option week-end
            6: ["* Option"],       # dimanche → option week-end
        }
        training_headers = ["**Plan d'entraînement", "**Plan d’entrainement", "**Plan d entrainement"]
    elif lang.startswith("es"):
        day_prefixes = {
            0: ["* Lunes"],        # lunes
            2: ["* Miércoles", "* Miercoles"],  # miércoles
            4: ["* Viernes"],      # viernes
            5: ["* Opcional"],     # sábado
            6: ["* Opcional"],     # domingo
        }
        training_headers = ["**Plan de entrenamiento"]
    else:
        # anglais (fallback)
        day_prefixes = {
            0: ["* Monday"],
            2: ["* Wednesday"],
            4: ["* Friday"],
            5: ["* Optional"],
            6: ["* Optional"],
        }
        training_headers = ["**Training plan"]

    prefixes_today = day_prefixes.get(today_idx)
    # Si on n'a pas de règle pour ce jour (ex. mardi/jeudi), on ne filtre pas
    if not prefixes_today:
        return answer

    lines = answer.splitlines()
    result: list[str] = []

    in_training_section = False

    for line in lines:
        stripped = line.strip()

        # Détection d'un titre de section Markdown : **...**
        if stripped.startswith("**") and stripped.endswith("**"):
            # Sommes-nous dans la section de plan d'entraînement ?
            if any(stripped.startswith(h) for h in training_headers):
                in_training_section = True
            else:
                # Autre section → on sort de la section entraînement
                in_training_section = False

            result.append(line)
            continue

        if in_training_section:
            # Dans la section entraînement :
            if stripped.startswith("*"):
                # Bullet avec jour de la semaine → garde seulement celui d'aujourd'hui
                keep = any(stripped.startswith(p) for p in prefixes_today)
                if keep:
                    result.append(line)
            else:
                # Texte normal dans la section entraînement → on garde
                result.append(line)
        else:
            # En dehors de la section entraînement → on garde tout
            result.append(line)

    return "\n".join(result)


# <<< NOVO: modèle + endpoint pour /reco/send-report >>>
class SendReportRequest(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    lang: Optional[str] = "fr"


@app.post("/reco/send-report")
async def send_report(req: SendReportRequest):
    """
    Récupère la dernière recommandation de l'utilisateur dans MongoDB,
    filtre le plan d'entraînement pour ne garder que la séance du jour,
    et ENVOIE réellement un e-mail au client.
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

    # 2) Récupérer la réponse IA brute
    answer = last_reco.get("answer", "") or ""
    lang = (req.lang or "fr").lower()

    # 3) Filtrer la partie plan d'entraînement pour ne garder que le jour actuel
    filtered_answer = filter_reco_for_today(answer, lang)

        # 4) Construire le contenu de l'e-mail
    subject = "Ton résumé personnalisé SportConnectIA"

    html_body = f"""\
<!DOCTYPE html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <title>Plan SportConnectIA</title>
  </head>
  <body style="margin:0;padding:0;background-color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0f172a;padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(15,23,42,0.25);">
            <!-- Header -->
            <tr>
              <td style="padding:24px 32px 16px;background:linear-gradient(135deg,#a855f7,#3b82f6);color:#f9fafb;">
                <h1 style="margin:0;font-size:24px;font-weight:800;">SportConnectIA</h1>
                <p style="margin:8px 0 0;font-size:14px;opacity:0.9;">
                  Ton plan personnalisé du jour
                </p>
              </td>
            </tr>

            <!-- Contenu principal -->
            <tr>
              <td style="padding:24px 32px 8px;color:#0f172a;font-size:14px;line-height:1.6;">
                <p style="margin:0 0 12px;">Bonjour {req.name or ''},</p>
                <p style="margin:0 0 16px;">
                  Voici le dernier résumé généré pour toi
                  <strong>(avec la séance du jour)</strong> :
                </p>

                <div style="margin:16px 0;padding:16px 18px;border-radius:12px;background:#f9fafb;border:1px solid #e5e7eb;">
                  <pre style="
                    margin:0;
                    font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                    font-size:13px;
                    white-space:pre-wrap;
                    color:#111827;
                  ">{filtered_answer}</pre>
                </div>

                <p style="margin:16px 0 0;font-size:12px;color:#6b7280;">
                  Ces recommandations sont indicatives et ne remplacent pas l’avis d’un professionnel de la santé.
                  Adapte toujours l’intensité à ton niveau et à ton ressenti.
                </p>

                <p style="margin:24px 0 0;">
                  À bientôt !<br/>
                  <span style="font-weight:600;">L’équipe SportConnectIA</span>
                </p>
              </td>
            </tr>

            <!-- Footer léger -->
            <tr>
              <td style="padding:12px 32px 20px;background:#f3f4f6;color:#9ca3af;font-size:11px;text-align:center;">
                Tu reçois cet e-mail parce que tu as généré un plan sur SportConnectIA.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


    # 5) Envoyer l'e-mail via SMTP
    try:
        send_email_smtp(req.email, subject, html_body)
        print(
            f"[RECO] Rapport envoyé par e-mail à {req.email} "
            f"(reco_id={last_reco.get('_id')})"
        )
    except Exception as e:
        print(f"[RECO] Erreur lors de l'envoi de l'e-mail: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'envoi de l'e-mail."
        )

    # 6) Réponse au frontend
    return {
        "ok": True,
        "message": "Rapport envoyé par e-mail.",
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
    1) Lit (ou crée) un profil utilisateur dans MongoDB
    2) Construit une question détaillée pour le Coach IA
    3) Appelle le microservice chatbot
    4) Sauvegarde la recommandation dans Firestore (si possible)
    5) Retourne { answer, profile } au frontend
    """
   # -------- Profil par défaut --------
    default_profile: Dict[str, Any] = {
        "name": "SportConnectIA",
        "age": 39,
        "weightKg": 64,
        "heightCm": 160,
        "mainGoal": "Perte de poids",
        "lang": "fr",
    }

    profile: Dict[str, Any] = default_profile.copy()

    # -------- 1) Lire ou créer le profil dans MongoDB --------
    try:
        user_doc = users_collection.find_one({"_id": req.user_id})

        if user_doc:
            profile.update({
                "name": user_doc.get("name") or profile["name"],
                "age": user_doc.get("age", profile["age"]),
                "weightKg": user_doc.get("weightKg", profile["weightKg"]),
                "heightCm": user_doc.get("heightCm", profile["heightCm"]),
                "mainGoal": user_doc.get("mainGoal") or profile["mainGoal"],
                "lang": user_doc.get("lang") or profile["lang"],
            })
        else:
            print(f"[RECO] Utilisateur {req.user_id} absent → création profil par défaut.")
            users_collection.insert_one({
                "_id": req.user_id,
                **default_profile
            })

    except Exception as e:
        # On log mais on continue avec le profil par défaut
        print(f"[RECO] Erreur MongoDB (lecture/écriture profil) : {e}")

    # langue finale (priorité : requête -> profil -> fr)
    lang = (req.lang or profile.get("lang") or "fr").lower()

    # -------- 2) Construire la question pour le Coach IA --------
    question = build_question_from_profile(profile)
    print(f"[RECO] Question envoyée au chatbot:\n{question}")

    # -------- 3) Appeler le microservice chatbot --------
    answer = await call_chatbot(question, lang)
    if not answer:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la réponse IA depuis le chatbot."
        )

    # -------- 4) Sauvegarder l'historique dans MongoDB --------
    from datetime import datetime as _dt

    try:
        reco_data = {
            "user_id": req.user_id,
            "question": question,
            "answer": answer,
            "createdAt": _dt.utcnow(),
            "age": profile.get("age"),
            "weightKg": profile.get("weightKg"),
            "heightCm": profile.get("heightCm"),
            "mainGoal": profile.get("mainGoal"),
            "lang": lang,
        }
        recommendations_collection.insert_one(reco_data)
        print(f"[RECO] Recommandation enregistrée pour user {req.user_id}.")
    except Exception as e:
        # On log l'erreur, mais on renvoie quand même la réponse au frontend
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
