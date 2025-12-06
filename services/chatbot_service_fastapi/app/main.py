# services/chatbot_service_fastapi/app/main.py

# -------------------------------------------------------
# Imports : système, FastAPI, CORS, modèles, HTTP, dotenv
# -------------------------------------------------------
import os
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# -------------------------------------------------------
# Charger le fichier .env à la racine du projet
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# -------------------------------------------------------
# Création du service FastAPI pour le chatbot
# -------------------------------------------------------
app = FastAPI(title="ChatbotService")

# -------------------------------------------------------
# CORS : autoriser le frontend Vite à accéder au service
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
# Config HuggingFace Router : modèle IA + token
# -------------------------------------------------------
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
HF_MODEL = os.getenv("HF_MODEL", "google/gemma-2-2b-it").strip()
HF_CHAT_URL = os.getenv(
    "HF_CHAT_URL",
    "https://router.huggingface.co/v1/chat/completions",
).rstrip("/")

MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "500"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

CHAT_PORT = int(os.getenv("CHATBOT_PORT") or os.getenv("PORT", "8004"))

print(
    f"HF Router -> model: {HF_MODEL} | token_len: "
    f"{len(HF_API_TOKEN) if HF_API_TOKEN else 0}"
)

if not HF_API_TOKEN:
    print("HF_API_TOKEN no está configurada, solo fallback local.")


# -------------------------------------------------------
# Modèle de la requête envoyée au chatbot
# -------------------------------------------------------
class AskRequest(BaseModel):
    message: str
    lang: Optional[str] = "es"
    profile: Optional[dict] = None


# -------------------------------------------------------
# Test rapide : vérifier que le service está vivo
# -------------------------------------------------------
@app.get("/chat/health")
async def health():
    return {"status": "ok", "service": "chat"}


# -------------------------------------------------------
# Prompt système : personalidad del Coach IA (AMPLIADO)
# -------------------------------------------------------
SYSTEM_PROMPT = (
    "Eres el Assistant Coach IA de SportConnectIA. "
    "Tu dominio es amplio dentro de la SALUD y el BIENESTAR FÍSICO y MENTAL, "
    "incluyendo:\n"
    "- deporte en general (deportes de equipo como fútbol, baloncesto, "
    "voleibol; deportes individuales como running, natación, ciclismo, tenis, etc.),\n"
    "- entrenamiento de fuerza y resistencia (gym, pesas, HIIT, cardio suave),\n"
    "- movilidad, estiramientos, flexibilidad, calentamiento y vuelta a la calma,\n"
    "- yoga, pilates, respiración, manejo del estrés y recuperación,\n"
    "- alimentación saludable, nutrición deportiva, hidratación, sueño y descanso.\n"
    "Tu misión es ayudar a la persona a entrenar mejor, sentirse más fuerte y "
    "llevar un estilo de vida equilibrado. Siempre que sea posible, propone:\n"
    "1) un plan o rutina sencilla y segura adaptada al nivel, objetivo y tiempo disponible,\n"
    "2) consejos de alimentación e hidratación razonables,\n"
    "3) recomendaciones de recuperación, sueño y gestión del estrés.\n"
    "Si no tienes suficiente información, haz primero 2 o 3 preguntas simples "
    "(nivel, frecuencia, lesiones, tiempo disponible).\n"
    "Sé prudente: empieza con intensidades moderadas, sugiere progresión gradual "
    "y recomienda consultar a un profesional de la salud en caso de dolor o "
    "condición médica. Si la pregunta está claramente fuera de estos temas "
    "(política, programación, chismes, etc.), rechaza amablemente en una o dos "
    "frases e invita a formular una pregunta sobre deporte, salud, yoga o nutrición.\n"
    "Responde SIEMPRE en el idioma del usuario."
)


# -------------------------------------------------------
# Palabras clave permitidas para filtrar preguntas (AMPLIADO)
# -------------------------------------------------------
ALLOWED_KEYWORDS = [
    # Español – salud / nutrición / bienestar
    "salud", "bienestar", "alimentación", "alimentacion", "nutrición", "nutricion",
    "dieta", "comida sana", "comida saludable", "calorías", "calorias",
    "proteína", "proteina", "proteínas", "proteinas",
    "carbohidratos", "grasas saludables", "hidratar", "hidratación", "suplemento",
    "suplementos", "vitaminas", "minerales",
    "sueño", "dormir", "descanso", "estrés", "estres", "ansiedad",
    # Español – entrenamiento / deportes
    "ejercicio", "entrenamiento", "rutina", "programa de entrenamiento",
    "deporte", "deportes", "cardio", "resistencia", "fuerza", "músculo",
    "musculo", "músculos", "musculos",
    "caminar", "correr", "running", "trote", "maratón", "maraton",
    "natación", "natacion", "nadar", "ciclismo", "bicicleta", "spinning",
    "gimnasio", "gym", "pesas", "levantamiento",
    "fútbol", "futbol", "baloncesto", "basket", "voleibol", "tenis",
    "flexibilidad", "movilidad", "estiramiento", "estiramientos", "stretching",
    "lesión", "lesiones", "dolor muscular", "agujetas",
    "yoga", "pilates", "respiración", "respiracion", "mindfulness",
    "meditación", "meditacion",

    # Français – santé / nutrition / bien-être
    "santé", "bien-être", "alimentation", "nutrition", "régime",
    "alimentation saine", "calories", "protéines", "glucides", "lipides",
    "hydratation", "suppléments", "vitamines", "minéraux",
    "sommeil", "dormir", "repos", "stress", "anxiété",
    # Français – sport / entraînement
    "exercice", "entraînement", "entrainement", "routine", "programme d'entraînement",
    "sport", "sports", "cardio", "endurance", "force", "musculation",
    "course", "footing", "running", "marathon",
    "natation", "vélo", "cyclisme", "vélo elliptique",
    "gym", "salle de sport", "haltères", "poids",
    "football", "basket", "basketball", "volley", "tennis",
    "souplesse", "mobilité", "étirements", "stretching",
    "blessure", "douleur musculaire",
    "yoga", "pilates", "respiration", "méditation",

    # English – health / nutrition / wellness
    "health", "wellbeing", "well-being", "healthy", "nutrition", "diet",
    "calories", "protein", "proteins", "carbs", "fats", "hydration",
    "supplement", "supplements", "vitamins", "minerals",
    "sleep", "rest", "recovery", "stress", "anxiety",
    # English – training / sports
    "exercise", "workout", "training", "training plan", "routine",
    "sport", "sports", "cardio", "endurance", "strength", "muscle", "muscles",
    "walk", "walking", "run", "running", "jog", "jogging", "marathon",
    "swim", "swimming", "bike", "biking", "cycling",
    "gym", "weights", "weight training",
    "football", "soccer", "basketball", "volleyball", "tennis",
    "flexibility", "mobility", "stretch", "stretching",
    "injury", "injuries", "muscle pain", "soreness",
    "yoga", "pilates", "breathing", "mindfulness", "meditation",
]


# -------------------------------------------------------
# Vérifie si la pregunta está relacionada con deporte/salud
# -------------------------------------------------------
def is_allowed_question(text: str) -> bool:
    """
    Devuelve True si el mensaje parece estar relacionado con
    salud, deporte, nutrición, bienestar, yoga, etc.
    El filtro es amplio para no bloquear preguntas útiles.
    """
    t = (text or "").lower().strip()

    # saludos / mensajes cortos al coach → dejar pasar
    if t in ["hola", "bonjour", "salut", "hello", "hi", "buenas", "bonsoir", "hey", "hola coach", "salut coach"]:
        return True

    # preguntas muy cortitas tipo "rutina gym", "plan yoga"
    if len(t) <= 15 and any(k in t for k in ["gym", "yoga", "sport", "deporte", "salud"]):
        return True

    # buscar cualquier palabra clave de nuestro dominio
    return any(k in t for k in ALLOWED_KEYWORDS)


# -------------------------------------------------------
# Respuesta básica si HuggingFace falla o no hay token
# -------------------------------------------------------
def fallback_answer(msg: str, lang: str) -> str:
    m = (msg or "").lower()

    # pequeño mensaje más “coach”
    if lang.startswith("fr"):
        return (
            "Dis-moi ton objectif (santé, perte de poids, prise de muscle, "
            "énergie, stress) et ton niveau actuel, et je te propose une "
            "routine simple (sport, yoga ou mobilité) 😊"
        )
    if lang.startswith("es"):
        return (
            "Cuéntame tu objetivo (salud, peso, músculo, energía o estrés) "
            "y tu nivel actual, y te propongo una rutina sencilla de deporte, "
            "cardio o yoga 😊"
        )
    return (
        "Tell me your goal (health, weight, muscle, energy or stress) and your "
        "current level, and I’ll propose a simple workout or yoga routine 😊"
    )


# -------------------------------------------------------
# Llamada al modelo IA en HuggingFace Router
# -------------------------------------------------------
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
                "content": f"Idioma / Lang / Langue du usuario: {lang}\n\nPregunta / Question: {question}",
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
    except Exception:
        return ""

    try:
        choices = data.get("choices") or []
        if not choices:
            return ""
        return (choices[0].get("message") or {}).get("content", "").strip()
    except Exception:
        return ""


# -------------------------------------------------------
# Endpoint principal : recibe pregunta → responde IA
# -------------------------------------------------------
@app.post("/chat/ask")
async def ask(req: AskRequest):
    msg = (req.message or "").strip()
    lang = (req.lang or "es").lower()

    if not msg:
        return {"answer": ""}

    # --- Filtrar dominio permitido (pero más amplio) ---
    if not is_allowed_question(msg):
        if lang.startswith("fr"):
            return {
                "answer": (
                    "Je suis l’Assistant Coach IA de SportConnectIA. "
                    "Je réponds uniquement sur le sport, la santé, la "
                    "nutrition, le bien-être, le yoga et la récupération. "
                    "Peux-tu reformuler ta question dans ce domaine ? 😊"
                )
            }
        if lang.startswith("es"):
            return {
                "answer": (
                    "Soy el Assistant Coach IA de SportConnectIA. "
                    "Respondo sobre deporte, salud, nutrición, bienestar, "
                    "yoga y recuperación. ¿Puedes reformular tu pregunta en "
                    "ese tema? 😊"
                )
            }
        return {
            "answer": (
                "I’m the SportConnectIA Assistant Coach. I answer questions "
                "about sport, health, nutrition, wellness, yoga and recovery. "
                "Please reformulate your question in that area 😊"
            )
        }

    # --- Llamar al modelo HF ---
    answer = await call_huggingface(msg, lang)

    # --- Si falla → fallback local ---
    if not answer:
        answer = fallback_answer(msg, lang)

    return {"answer": answer}


# -------------------------------------------------------
# Ejecutar el servicio directamente con Python
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=CHAT_PORT, reload=True)
