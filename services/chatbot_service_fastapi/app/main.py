# services/chatbot_service_fastapi/app/main.py
import os
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# =========================
#   Cargar .env de la raíz
# =========================
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

app = FastAPI(title="ChatbotService")

# === CORS para Vite (frontend) ===
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

# === Config Hugging Face – Router (chat-completion) ===
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
HF_MODEL = os.getenv("HF_MODEL", "google/gemma-2-2b-it").strip()
HF_CHAT_URL = os.getenv(
    "HF_CHAT_URL",
    "https://router.huggingface.co/v1/chat/completions",
).rstrip("/")

MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "500"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

CHAT_PORT = int(os.getenv("CHAT_PORT") or os.getenv("PORT", "8010"))

print(
    f"HF Router -> model: {HF_MODEL} | token_len: "
    f"{len(HF_API_TOKEN) if HF_API_TOKEN else 0}"
)
if not HF_API_TOKEN:
    print("HF_API_TOKEN no está configurada, solo se usará el fallback local.")


class AskRequest(BaseModel):
    message: str
    lang: Optional[str] = "es"
    profile: Optional[dict] = None


@app.get("/chat/health")
async def health():
    return {"status": "ok", "service": "chat"}


# ============================
#  System prompt (personalidad)
# ============================
SYSTEM_PROMPT = (
    "Eres el Assistant Coach IA de SportConnectIA. "
    "Solo puedes responder sobre SALUD, ALIMENTACIÓN SANA, NUTRICIÓN, "
    "DEPORTE, ENTRENAMIENTO FÍSICO, YOGA, RECUPERACIÓN, MOTIVACIÓN DEPORTIVA "
    "y EVENTOS/COMPETICIONES DEPORTIVAS. "
    "Tu principal misión es ayudar a la persona a entrenar mejor y llevar "
    "un estilo de vida saludable. "
    "Siempre que sea posible, propone ENTRENAMIENTOS SUGERIDOS adaptados "
    "a la persona (nivel principiante, intermedio o avanzado, edad "
    "aproximada, objetivo: perder peso, ganar músculo, salud general, "
    "rendimiento, etc.). "
    "Si no tienes suficiente información para personalizar el plan, "
    "haz primero 2 o 3 preguntas sencillas (por ejemplo: nivel actual, "
    "frecuencia de entrenamiento, lesiones o dolores importantes) y luego "
    "propón una rutina simple y segura. "
    "Tus recomendaciones deben ser prudentes: empieza suave, aumenta "
    "progresivamente la carga y recomienda consultar a un profesional de "
    "la salud en caso de dolor, enfermedad o condición médica. "
    "Si la pregunta no está relacionada con esos temas, debes negarte "
    "amablemente en UNA o DOS frases y pedir que reformule una pregunta "
    "sobre deporte, salud, nutrición o yoga. "
    "Sé conciso, claro e inclusivo y responde SIEMPRE en el idioma del usuario."
)

# ============================
#  Filtro de dominios permitidos
# ============================

ALLOWED_KEYWORDS = [
    # Español
    "salud", "alimentación", "alimentacion", "nutrición", "nutricion",
    "comida sana", "dieta", "ejercicio", "entrenamiento", "rutina",
    "programa de entrenamiento", "plan de entrenamiento",
    "deporte", "correr", "carrera", "caminar", "gimnasio", "fuerza", "cardio",
    "yoga", "pilates", "partido", "torneo", "competición", "competicion",
    "maratón", "maraton",

    # Francés
    "santé", "alimentation", "nutrition", "régime", "exercice",
    "entraînement", "entrainement", "programme d'entraînement",
    "routine d'entraînement", "sport", "musculation", "course",
    "marche", "gym", "cardio", "yoga", "pilates",
    "match", "tournoi", "compétition",

    # Inglés
    "health", "healthy food", "nutrition", "diet",
    "workout", "training", "training plan", "workout plan", "routine",
    "exercise", "sport", "gym", "running", "walking", "cardio",
    "yoga", "pilates", "match", "tournament", "competition",
]


def is_allowed_question(text: str) -> bool:
    """
    Devuelve True si el mensaje parece estar relacionado con
    salud, alimentación sana, deporte, entrenamiento o eventos deportivos.
    """
    t = (text or "").lower().strip()

    # Dejar pasar saludos simples (el modelo responderá algo deportivo)
    if t in ["hola", "bonjour", "salut", "hello", "hi", "buenas", "bonsoir"]:
        return True

    return any(k in t for k in ALLOWED_KEYWORDS)


# ============================
#  Fallback local sencillo
# ============================
def fallback_answer(msg: str, lang: str) -> str:
    m = msg.lower()
    if any(
        w in m
        for w in [
            "deporte", "ejercicio", "sport", "exercise", "entrenar",
            "training", "entrenamiento", "rutina", "plan", "yoga"
        ]
    ):
        if lang.startswith("es"):
            return (
                "Puedes empezar hoy con una caminata ligera de 20–30 minutos, "
                "un poco de movilidad articular y 2–3 series de sentadillas, "
                "plancha y puente de glúteos (10–12 repeticiones). "
                "Si te interesa el yoga, comienza con 10–15 minutos de posturas "
                "suaves (como el perro boca abajo, el gato-vaca y la postura del niño) "
                "y enfócate en respirar de forma lenta y profunda. "
                "Acompáñalo con agua, frutas, verduras y proteínas magras. "
                "Cuéntame tu nivel (principiante, intermedio), tu objetivo "
                "(bajar de peso, ganar músculo, salud, flexibilidad) y cuántos días puedes "
                "entrenar a la semana para afinar mejor tu rutina 😊"
            )
        if lang.startswith("fr"):
            return (
                "Commence par 20–30 minutes de marche, un peu de mobilité, "
                "puis 2–3 séries de squats, planche et pont fessier "
                "(10–12 répétitions). "
                "Si tu t'intéresses au yoga, démarre avec 10–15 minutes de postures "
                "douces (chien tête en bas, chat-vache, posture de l’enfant) "
                "en respirant calmement. "
                "Ajoute beaucoup d’eau, des fruits, des légumes et des "
                "protéines maigres. "
                "Dis-moi ton niveau (débutant, intermédiaire), ton objectif "
                "(perte de poids, prise de muscle, santé, souplesse) et le nombre de "
                "jours par semaine pour personnaliser ta routine 😊"
            )
        return (
            "You can start with a 20–30 minute light walk, some mobility work, "
            "and 2–3 sets of squats, plank and glute bridge (10–12 reps). "
            "If you are interested in yoga, begin with 10–15 minutes of gentle "
            "poses (like downward dog, cat-cow and child’s pose) with slow breathing. "
            "Combine it with water, fruits, vegetables and lean protein. "
            "Tell me your level (beginner, intermediate), your goal "
            "(fat loss, muscle gain, health, flexibility) and how many days per week you "
            "can train so I can personalize your routine 😊"
        )

    if lang.startswith("es"):
        return (
            "Cuéntame tu objetivo (salud, fuerza, peso, yoga, tiempo disponible) "
            "y armamos un plan rápido 😊"
        )
    if lang.startswith("fr"):
        return (
            "Dis-moi ton objectif (santé, force, poids, yoga, temps disponible) "
            "et on crée un plan rapide 😊"
        )
    return (
        "Tell me your goal (health, strength, weight, yoga, time) "
        "and we’ll create a quick plan 😊"
    )


# ============================
#  Llamada al Router HF
# ============================
async def call_huggingface(question: str, lang: str) -> str:
    if not HF_API_TOKEN:
        return ""

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": HF_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Idioma del usuario: {lang}\n\nPregunta: {question}",
            },
        ],
        "max_tokens": MAX_RESPONSE_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
    }

    try:
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.post(HF_CHAT_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print(f"Error llamando a Hugging Face Router: {e}")
        return ""

    try:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content") or ""
        return str(content).strip()
    except Exception as e:
        print(f"Error parseando respuesta de Hugging Face: {e}")
        return ""


# ============================
#  Endpoint principal
# ============================
@app.post("/chat/ask")
async def ask(req: AskRequest):
    msg = (req.message or "").strip()
    lang = (req.lang or "es").lower()

    if not msg:
        return {"answer": ""}

    # --- 1) Filtro de dominio ---
    if not is_allowed_question(msg):
        if lang.startswith("fr"):
            return {
                "answer": (
                    "Je suis l’Assistant Coach IA de SportConnectIA. "
                    "Je peux seulement répondre sur la santé, "
                    "l’alimentation saine, la nutrition sportive, "
                    "l’entraînement, le yoga ou des événements sportifs. "
                    "Peux-tu reformuler ta question dans ce domaine ? 🙂"
                )
            }
        if lang.startswith("es"):
            return {
                "answer": (
                    "Soy el Assistant Coach IA de SportConnectIA. "
                    "Solo puedo responder sobre salud, alimentación sana, "
                    "nutrición deportiva, entrenamiento, yoga o eventos deportivos. "
                    "Por favor, reformula tu pregunta en ese tema 🙂"
                )
            }
        return {
            "answer": (
                "I am the SportConnectIA Assistant Coach. I can only answer "
                "questions about health, healthy eating, sports training, yoga "
                "or sport events. Please reformulate your question in that "
                "area 🙂"
            )
        }

    # --- 2) Pregunta aceptada → modelo HF ---
    answer = await call_huggingface(msg, lang)

    # --- 3) Si falla o viene vacío → fallback local ---
    if not answer or not answer.strip():
        answer = fallback_answer(msg, lang)

    return {"answer": answer.strip()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=CHAT_PORT, reload=True)
