import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

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

PORT = int(os.getenv("PORT", "8010"))

print(f"HF Router -> model: {HF_MODEL} | token_len: {len(HF_API_TOKEN) if HF_API_TOKEN else 0}")
if not HF_API_TOKEN:
    print("HF_API_TOKEN no está configurado, solo se usará el fallback local.")


class AskRequest(BaseModel):
    message: str
    lang: Optional[str] = "es"
    profile: Optional[dict] = None


@app.get("/chat/health")
async def health():
    return {"status": "ok", "service": "chat"}


SYSTEM_PROMPT = (
    "Eres un coach deportivo conciso, claro e inclusivo. "
    "Da consejos seguros para personas principiantes o intermedias. "
    "Sugiere empezar suave e incrementar poco a poco. "
    "Responde SIEMPRE en el idioma del usuario."
)


# ============================
#  Fallback local sencillo
# ============================
def fallback_answer(msg: str, lang: str) -> str:
    m = msg.lower()
    if any(
        w in m
        for w in ["deporte", "ejercicio", "sport", "exercise", "entrenar", "training"]
    ):
        if lang.startswith("es"):
            return (
                "Puedes empezar hoy con una caminata ligera de 20–30 minutos, "
                "un poco de movilidad articular y 2–3 series de sentadillas, "
                "plancha y puente de glúteos (10–12 repeticiones). "
                "Aumenta poco a poco cada semana."
            )
        if lang.startswith("fr"):
            return (
                "Commence par 20–30 minutes de marche, un peu de mobilité, "
                "puis 2–3 séries de squats, planche et pont fessier (10–12 répétitions)."
            )
        return (
            "Start with a 20–30 minute walk, some mobility work, and 2–3 rounds "
            "of squats, plank, and glute bridge (10–12 reps)."
        )

    if lang.startswith("es"):
        return "Cuéntame tu objetivo (salud, fuerza, peso, tiempo disponible) y armamos un plan rápido 😊"
    if lang.startswith("fr"):
        return "Dis-moi ton objectif (santé, force, poids, temps disponible) et on crée un plan rapide 😊"
    return "Tell me your goal (health, strength, weight, time) and we’ll create a quick plan 😊"


# ============================
#  Llamada al Router HF
# ============================
async def call_huggingface(question: str, lang: str) -> str:
    # Llama al Router de Hugging Face (Inference Providers, chat-completion)
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

    # 1) Intentar con modelo avanzado de HF
    answer = await call_huggingface(msg, lang)

    # 2) Si falla o viene vacío → usamos fallback local
    if not answer or not answer.strip():
        answer = fallback_answer(msg, lang)

    return {"answer": answer.strip()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
