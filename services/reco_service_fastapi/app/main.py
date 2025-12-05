from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import json
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from .tracking_db import init_db, get_conn

load_dotenv()

# === Inicializar BD ao arrancar ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
  

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# ------------ FUNÇÃO AUXILIAR PARA EMAIL ------------

def send_email_smtp(to_email: str, subject: str, body: str):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL") or username or "no-reply@sportconnectia.local"

    # aqui usamos o parâmetro `body`, que no seu caso já é HTML
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # 1) Se NÃO houver SMTP configurado → modo DEBUG
    if not host or not username or not password:
        print("=== DEBUG EMAIL SPORTCONNECTIA ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("Body:\n", body)
        print("=== FIN DEBUG EMAIL ===")
        return

    # 2) Envio real via SMTP
    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

        print("✅ E-mail enviado via SMTP para", to_email)

    except Exception as e:
        print("Erro ao enviar e-mail via SMTP, caindo em modo DEBUG:", e)
        print("=== DEBUG EMAIL SPORTCONNECTIA (FALLBACK) ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("Body:\n", body)
        print("=== FIN DEBUG EMAIL (FALLBACK) ===")



# ------------ MODELOS TRACKING ------------

class MeasurementIn(BaseModel):
    date: str
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    notes: Optional[str] = None


class MeasurementOut(MeasurementIn):
    id: int


# ------------ MODELOS RECOMENDACIONES ----------

class RecommendationRequest(BaseModel):
    user_id: str
    email: Optional[str] = None
    type: Optional[str] = None  # e.g., "nutrition", "workout", "general"
    lang: Optional[str] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    main_goal: Optional[str] = None
    days_per_week: Optional[int] = None
    minutes_per_session: Optional[int] = None
    level: Optional[str] = None
    data: Optional[dict] = None


class RecommendationOut(BaseModel):
    id: int
    user_id: str
    email: str
    type: str
    content: str
    created_at: str
    metadata: Optional[dict] = None


class EmailReportRequest(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    lang: Optional[str] = None


# ------------ ENDPOINTS TRACKING ------------

@app.post("/tracking/measurements", response_model=dict)
def add_measurement(
    email: str = Query(...),      # vem de ?email=...
    body: MeasurementIn = ...,    # vem do JSON
):
    if not body.date:
        raise HTTPException(status_code=400, detail="date is required")

    try:
        with get_conn() as c:
            cur = c.cursor()
            cur.execute(
                """
                INSERT INTO measurements(email, date, weight_kg, waist_cm, hips_cm, chest_cm, notes)
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
    except Exception as e:
        print(" Erro ao inserir measurement:", e)
        raise HTTPException(
            status_code=500,
            detail=f"DB error while saving measurement: {str(e)}",
        )


# ------------ ENDPOINTS RECOMENDACIONES ----------

@app.post("/reco/generate", response_model=dict)
def generate_recommendation(body: RecommendationRequest):
    """
    Gera uma recomendação "fixa" baseada nos dados do usuário
    e TENTA salvar no SQLite. Mesmo que o save falhe, SEMPRE retorna a recomendação.
    """

    # Usar email do body ou gerar um fake interno (não é destino do e-mail!)
    email = body.email or f"user_{body.user_id}@sportconnect.local"

    # Determinar tipo de recomendación
    reco_type = body.type or body.main_goal or "general"

    goal = body.main_goal or "remise en forme"
    days = body.days_per_week or 3
    minutes = body.minutes_per_session or 45

    content = f"""**Plan:**
Salut ! Je peux t'aider à atteindre tes objectifs de {goal} avec un programme d'entraînement simple, progressif et adapté à ton niveau, accompagné de conseils nutritionnels et de récupération.

**Plan d'entraînement ({days} séances par semaine max):**
*Lundi:** {minutes} minutes de marche rapide ou de vélo léger, suivies de quelques étirements.
*Mercredi:** {minutes} minutes de HIIT (High Intensity Interval Training) avec des exercices comme jumping jacks, burpees modifiés et montées de genoux.
*Vendredi:** {minutes} minutes de cardio doux (vélo elliptique, natation ou marche en côte) + 5–10 minutes d'étirements.

**Conseils d'alimentation et d'hydratation:**
*Hydratez-vous:** Buvez de l'eau régulièrement tout au long de la journée, surtout avant, pendant et après l'exercice.
*Mangez des aliments riches en protéines:** Poulet, poisson, œufs, légumineuses et yaourts pour soutenir la masse musculaire.
*Priorisez les fruits et légumes:** Ils apportent fibres, vitamines et minéraux essentiels.
*Limitez les aliments ultra-transformés:** Snacks industriels, boissons sucrées et fast-foods.
*Contrôlez les portions:** Mange lentement, en écoutant tes sensations de faim et de satiété.

**Conseil de récupération/sommeil/motivation:**
*Dormez suffisamment:** 7 à 8 heures de sommeil réparateur par nuit.
*Gérez le stress:** Pratique des activités relaxantes comme la méditation, la respiration profonde ou le yoga doux.
*Fixe-toi des objectifs réalistes:** Commence petit, progresse étape par étape et célèbre chaque petite victoire.

**Important:**
Avant de commencer un nouveau programme d'entraînement, il est toujours recommandé de consulter un professionnel de la santé, surtout en cas de problème médical. Adapte l'intensité selon ton ressenti et n'hésite pas à redemander une nouvelle recommandation si tes objectifs évoluent.
"""

    metadata_dict = {
        "age": body.age,
        "weight_kg": body.weight_kg,
        "height_cm": body.height_cm,
        "main_goal": body.main_goal,
        "level": body.level,
        "lang": body.lang,
    }

    now_iso = datetime.utcnow().isoformat()
    new_id = None

    # TENTA salvar na BD, mas NÃO quebra se der erro
    try:
        with get_conn() as c:
            cur = c.cursor()
            metadata_json = json.dumps(metadata_dict)
            cur.execute(
                """
                INSERT INTO recommendations(user_id, email, type, content, created_at, metadata)
                VALUES(?,?,?,?,?,?)
                """,
                (
                    body.user_id,
                    email.lower(),
                    reco_type,
                    content,
                    now_iso,
                    metadata_json,
                ),
            )
            c.commit()
            new_id = cur.lastrowid
    except Exception as e:
        print("⚠️ ERRO AO SALVAR RECOMENDAÇÃO NO SQLITE:", e)

    # Mesmo que o INSERT dê erro, devolvemos a recomendação pro frontend
    return {
        "ok": True,
        "id": new_id,
        "type": reco_type,
        "content": content,
        "answer": content,
        "created_at": now_iso,
        "metadata": metadata_dict,
    }


@app.post("/reco/send-report", response_model=dict)
def send_daily_report(body: EmailReportRequest):

    email = body.email.lower()
    today_str = date.today().isoformat()

    try:
        with get_conn() as c:
            cur = c.cursor()

            cur.execute(
                """
                SELECT date, weight_kg, waist_cm, hips_cm, chest_cm, notes
                FROM measurements
                WHERE email=? AND date=?
                ORDER BY id DESC
                """,
                (email, today_str),
            )
            measures_today = [dict(r) for r in cur.fetchall()]

            cur.execute(
                """
                SELECT id, content, created_at
                FROM recommendations
                WHERE user_id=? AND email=?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (body.user_id, email),
            )
            last_reco_row = cur.fetchone()

    except Exception as e:
        print("⚠️ ERRO AO LER DADOS PARA /reco/send-report:", e)
        measures_today = []
        last_reco_row = None

    raw_name = (body.name or email.split("@")[0]).strip()
    civ = "Mme" if raw_name.lower().endswith("a") else "M"
    salutation = f"Bonjour {civ} {raw_name}"

    # ------------------ CORREÇÃO 1: mesures_txt ------------------
    if measures_today:
        m = measures_today[0]
        mesures_txt = (
            f"- Date : {m['date']}\n"
            f"- Poids (kg) : {m.get('weight_kg', '—')}\n"
            f"- Tour de taille (cm) : {m.get('waist_cm', '—')}\n"
            f"- Tour de hanches (cm) : {m.get('hips_cm', '—')}\n"
            f"- Tour de poitrine (cm) : {m.get('chest_cm', '—')}\n"
        )
        if m.get("notes"):
            mesures_txt += f"- Notes : {m['notes']}\n"
    else:
        mesures_txt = "Aucune mesure enregistrée aujourd'hui.\n"

    # ------------------ CORREÇÃO 2: reco_txt ------------------
    if last_reco_row:
        last_reco = dict(last_reco_row)
        reco_txt = last_reco["content"]
        reco_date = last_reco["created_at"]
    else:
        reco_txt = "Aucune recommandation enregistrée pour le moment."
        reco_date = "—"

    # ------------------ CORREÇÃO 3: preparar HTML antes ------------------
    mesures_html = mesures_txt.replace("\n", "<br>")
    reco_html = reco_txt.replace("\n", "<br>")

    # ------------------ CORREÇÃO 4: usar as variáveis no HTML ------------------
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8" />
    <style>
        body {{
        font-family: Arial, sans-serif;
        background: #f4f7fb;
        padding: 0;
        margin: 0;
        }}
        .container {{
        max-width: 600px;
        background: #ffffff;
        margin: 20px auto;
        border-radius: 16px;
        padding: 24px 28px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }}
        h1 {{
        color: #1e3a8a;
        font-size: 20px;
        margin-bottom: 12px;
        }}
        .section-title {{
        font-size: 16px;
        font-weight: bold;
        color: #be185d;
        margin-top: 24px;
        margin-bottom: 8px;
        }}
        .metrics-box {{
        background: #fdf2f8;
        border-left: 5px solid #ec4899;
        padding: 12px 16px;
        border-radius: 10px;
        font-size: 14px;
        line-height: 1.4;
        }}
        .reco-box {{
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 10px;
        font-size: 14px;
        white-space: pre-line;
        line-height: 1.4;
        }}
        .footer {{
        margin-top: 28px;
        font-size: 12px;
        color: #6b7280;
        text-align: center;
        }}
    </style>
    </head>

    <body>
    <div class="container">
        <h1>🏋️‍♀️ SportConnectIA – Rapport Quotidien</h1>

        <p>{salutation},</p>
        <p>Voici ton rapport SportConnectIA pour aujourd’hui <strong>({today_str})</strong>.</p>

        <div class="section-title">1) Résumé de tes mesures du jour</div>
        <div class="metrics-box">
            {mesures_html}
        </div>

        <div class="section-title">2) Dernière recommandation IA</div>
        <p style="font-size:12px; color:#6b7280; margin-bottom:4px;">
        Générée le {reco_date}
        </p>
        <div class="reco-box">
            {reco_html}
        </div>

        <p class="footer">
        Merci de ta confiance 💙<br>
        L'équipe SportConnectIA 🤖💪
        </p>
    </div>
    </body>
    </html>
    """

    subject = "Ton rapport quotidien SportConnectIA"

    try:
        send_email_smtp(email, subject, body_html)
        return {"ok": True, "message": "Rapport envoyé"}
    except Exception as e:
        print("⚠️ ERRO AO ENVIAR E-MAIL EM /reco/send-report:", e)
        return {"ok": False, "message": "Erreur interne lors de l'envoi du rapport."}


@app.get("/reco/history/{user_id}", response_model=List[RecommendationOut])
def get_recommendation_history(user_id: str, email: str = Query(None)):
    try:
        with get_conn() as c:
            cur = c.cursor()
            if email:
                cur.execute(
                    """
                    SELECT id, user_id, email, type, content, created_at, metadata
                    FROM recommendations
                    WHERE user_id=? AND email=?
                    ORDER BY created_at DESC
                    """,
                    (user_id, email.lower()),
                )
            else:
                cur.execute(
                    """
                    SELECT id, user_id, email, type, content, created_at, metadata
                    FROM recommendations
                    WHERE user_id=?
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )
            rows = cur.fetchall()

        result = []
        for row in rows:
            rec = dict(row)
            if rec["metadata"]:
                rec["metadata"] = json.loads(rec["metadata"])
            result.append(rec)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching recommendation history: {str(e)}"
        )


@app.get("/reco/history", response_model=List[RecommendationOut])
def get_all_recommendations(email: str = Query(...)):
    try:
        with get_conn() as c:
            cur = c.cursor()
            cur.execute(
                """
                SELECT id, user_id, email, type, content, created_at, metadata
                FROM recommendations
                WHERE email=?
                ORDER BY created_at DESC
                """,
                (email.lower(),),
            )
            rows = cur.fetchall()

        result = []
        for row in rows:
            rec = dict(row)
            if rec["metadata"]:
                rec["metadata"] = json.loads(rec["metadata"])
            result.append(rec)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching recommendations: {str(e)}"
        )


@app.get("/reco/test", response_model=dict)
def test_recommendations():
    try:
        with get_conn() as c:
            cur = c.cursor()
            cur.execute("SELECT COUNT(*) as count FROM recommendations")
            count = cur.fetchone()["count"]

            cur.execute(
                """
                SELECT id, user_id, email, type, content, created_at
                FROM recommendations
                ORDER BY created_at DESC
                LIMIT 5
                """
            )
            recent = [dict(r) for r in cur.fetchall()]

        return {"total_recommendations": count, "recent": recent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
