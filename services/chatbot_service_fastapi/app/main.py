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
    history: Optional[list] = None


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
    "Si el usuario responde a una de tus preguntas, usa su respuesta para adaptar tus consejos "
    "y NO repitas la misma pregunta. Avanza paso a paso y mantén una conversación coherente.\n"
)


# -------------------------------------------------------
# Palabras clave permitidas para filtrar preguntas (AMPLIADO)
# -------------------------------------------------------
ALLOWED_KEYWORDS = [
    #português – saúde / nutrição / bem-estar
    "saúde", "bem-estar", "alimentação", "nutrição", "dieta",
    "comida saudável", "calorias", "proteínas", "carboidratos", "gorduras",
    "hidratação", "suplementos", "vitaminas", "minerais",
    "sono", "dormir", "descanso", "estresse", "ansiedade", "fadiga",
    "dor muscular", "saúde mental", "hábitos saudáveis", "estilo de vida",
    "bem-estar mental", "gestão do estresse", "relaxamento",
    #português – treino / esportes
    "exercício", "treino", "rotina", "plano de treino",
    "esporte", "esportes", "cardio", "resistência", "força", "musculação",
    "caminhar", "corrida", "maratona","natação", "ciclismo", "academia",
    "pesos", "levantamento de peso", "futebol", "basquete", "vôlei", "tênis",
    "flexibilidade", "mobilidade", "alongamento", "lesão", "dor muscular",
    "yoga", "pilates", "respiração", "meditação", "mindfulness",    
    "dança", "relaxamento", "meditação guiada","gestão do estresse", "depressao",
    "ansiedade","saúde mental","depressão", "exercícios de respiração", "exercícios para ansiedade",
    "exercicios pesados",
    # Español – salud / nutrición / bienestar
    "salud", "bienestar", "alimentación", "alimentacion", "nutrición", "nutricion",
    "dieta", "comida sana", "comida saludable", "calorías", "calorias",
    "proteína", "proteina", "proteínas", "proteinas",
    "carbohidratos", "grasas saludables", "hidratar", "hidratación", "suplemento",
    "suplementos", "vitaminas", "minerales",
    "sueño", "dormir", "descanso", "estrés", "estres", "ansiedad", "fatiga",
    "dolor muscular", "salud mental", "hábitos saludables", "habitos saludables",
    "estilo de vida", "bienestar mental", "gestion del estrés", "gestion del estres",
    "relajación", "relajacion","manejo del estrés","manejo del estres","salud emocional",
    "salud fisica","salud física",
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
    "meditación", "meditacion", "dance", "danza", "relajación", "relajacion",
    "meditación guiada","meditacion guiada","manejo del estrés","manejo del estres",
    "recuperación","recuperacion","salud fisica","salud física",

    # Français – santé / nutrition / bien-être
    "santé", "bien-être", "alimentation", "nutrition", "régime",
    "alimentation saine", "calories", "protéines", "glucides", "lipides",
    "hydratation", "suppléments", "vitamines", "minéraux",
    "sommeil", "dormir", "repos", "stress", "anxiété", "fatigue",
    "douleur", "anxiété", "gestion du stress",
    "récupération", "recuperation", "relaxation", "repos", "bien-être mental",
    "santé mentale", "habitudes de vie","mode de vie sain", "habitudes saines",
    "gestion du stress", "relaxation","pleine conscience","mindfulness","méditation guidée",
    "santé physique","santé mentale","dépression","anxiété","exercices de respiration"
    # Français – sport / entraînement
    "exercice", "entraînement", "entrainement", "routine", "programme d'entraînement",
    "sport", "sports", "cardio", "endurance", "force", "musculation",
    "course", "footing", "running", "marathon",
    "natation", "vélo", "cyclisme", "vélo elliptique","danse",
    "gym", "salle de sport", "haltères", "poids",
    "football", "basket", "basketball", "volley", "tennis",
    "souplesse", "mobilité", "étirements", "stretching",
    "blessure", "douleur musculaire",
    "yoga", "pilates", "respiration", "méditation", "pleine conscience",
    "relaxation","méditation guidée","mindfulness", "gestion du stress","gestion du stress",
    "récupération","recuperation","santé physique","santé mentale","exercices pour l'anxiété",
    "exercices intenses","exercices lourds","dépression"

    # English – health / nutrition / wellness
    "health", "wellbeing", "well-being", "healthy", "nutrition", "diet",
    "calories", "protein", "proteins", "carbs", "fats", "hydration",
    "supplement", "supplements", "vitamins", "minerals",
    "sleep", "rest", "recovery", "stress", "anxiety"," fatigue",
    "muscle pain", "mental health", "lifestyle", "healthy habits",
    "mental wellbeing", "mental well-being","stress", "relaxation",
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
    "dance", "relaxation", "guided meditation"," mindfulness", "stress management",
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
#  👉 AQUI estávamos devolviendo “Dis-moi ton objectif…”
#  Agora devolvemos un plan completo en 4 secciones (Markdown)
# -------------------------------------------------------
def fallback_answer(msg: str, lang: str) -> str:
    m = (msg or "").lower()

    if lang.startswith("fr"):
        return (
            "**Plan**\n"
            "* Salut ! À partir de ton profil et de ton objectif de remise en forme, je te propose un programme d'entraînement simple, progressif et adaptable à ton niveau.\n"
            "* L’idée est de bouger régulièrement, de renforcer tout le corps et d’adopter quelques bonnes habitudes d’alimentation et de récupération.\n\n"
            "**Plan d'entraînement (3 séances par semaine max)**\n"
            "* Lundi : 30–40 minutes de marche rapide ou de vélo léger, suivies de 5–10 minutes d’étirements doux (jambes, dos, épaules).\n"
            "* Mercredi : 30 minutes de renforcement musculaire (squats au poids du corps, fentes, pompes adaptées contre un mur ou sur les genoux, gainage 3×20–30 s).\n"
            "* Vendredi : 30–40 minutes d’activité cardio au choix (marche en côte, vélo, natation douce ou cours de yoga dynamique), puis respiration profonde et étirements.\n"
            "* Option : si tu te sens bien, ajoute une courte séance de mobilité le weekend (10–15 minutes d’étirements et de mouvements articulaires).\n\n"
            "**Conseils d'alimentation et d’hydratation**\n"
            "* Bois de l’eau régulièrement dans la journée (6 à 8 verres), et un peu avant/après l’entraînement.\n"
            "* Compose tes repas autour de trois piliers : une source de protéines (œufs, poisson, tofu, légumineuses), des légumes variés et un féculent complet (riz complet, quinoa, patate douce, pain complet).\n"
            "* Limite les produits ultra-transformés, très sucrés ou très gras (boissons gazeuses, fast-food, snacks industriels) à un usage occasionnel.\n"
            "* Privilégie des collations simples : fruit frais, yaourt nature, poignée de noix ou d’amandes.\n"
            "* Essaie de garder des horaires de repas assez réguliers pour stabiliser ton énergie dans la journée.\n\n"
            "**Conseil de récupération/sommeil/motivation**\n"
            "* Vise 7 à 8 heures de sommeil par nuit, dans une chambre calme, sombre et fraîche (éloigne les écrans au moins 30 minutes avant de dormir).\n"
            "* Après chaque séance, prends 5–10 minutes pour respirer profondément et t’étirer : cela aide à détendre les muscles et le mental.\n"
            "* Écoute ton corps : en cas de douleur inhabituelle, diminue l’intensité ou remplace l’exercice par un mouvement plus doux.\n"
            "* Fixe-toi de petits objectifs concrets (par exemple : marcher 3 fois par semaine pendant un mois) et note tes progrès.\n"
            "* N’hésite pas à demander l’avis d’un professionnel de santé si tu as un problème médical ou une douleur persistante.\n"
        )

    if lang.startswith("es"):
        return (
            "**Plan**\n"
            "* A partir de tu objetivo de ponerte en forma, te propongo una rutina sencilla, progresiva y realista que puedas mantener en el tiempo.\n"
            "* La idea es moverte de forma regular, trabajar fuerza básica y cuidar la alimentación y el descanso.\n\n"
            "**Plan de entrenamiento (3 sesiones por semana máximo)**\n"
            "* Lunes: 30–40 minutos de caminata rápida o bicicleta suave, seguidos de 5–10 minutos de estiramientos.\n"
            "* Miércoles: 30 minutos de fuerza con el propio peso (sentadillas, zancadas, flexiones apoyadas en pared o rodillas, plancha 3×20–30 s).\n"
            "* Viernes: 30–40 minutos de cardio a tu elección (caminata en subida, bici, natación suave o yoga dinámico) + respiración profunda.\n"
            "* Opcional: el fin de semana, 10–15 minutos de movilidad y estiramientos suaves para relajar el cuerpo.\n\n"
            "**Consejos de alimentación e hidratación**\n"
            "* Bebe agua a lo largo del día (6–8 vasos) y alrededor del entrenamiento.\n"
            "* Llena tu plato con: una fuente de proteína (huevos, pescado, legumbres, tofu), verduras de colores y un carbohidrato integral (arroz integral, quinoa, avena, pan integral).\n"
            "* Reduce los ultraprocesados, refrescos azucarados y “fast-food” a ocasiones puntuales.\n"
            "* Elige colaciones simples: fruta fresca, yogur natural, un puñado de frutos secos.\n"
            "* Intenta mantener horarios de comida relativamente regulares para estabilizar tu energía.\n\n"
            "**Consejos de recuperación/sueño/motivación**\n"
            "* Intenta dormir 7–8 horas por noche en un ambiente oscuro y tranquilo, alejando pantallas antes de acostarte.\n"
            "* Después de entrenar, dedica unos minutos a estirarte y respirar profundo para soltar tensión.\n"
            "* Escucha tu cuerpo: si notas dolor raro, baja la intensidad o cambia el ejercicio por una variante más suave.\n"
            "* Márcate objetivos pequeños y medibles (por ejemplo, caminar 3 veces por semana) y celebra tus avances.\n"
            "* Si tienes una condición médica o un dolor persistente, consulta con un profesional de la salud.\n"
        )

    # Inglés (fallback general)
    return (
        "**Plan**\n"
        "* Based on your goal of getting fitter, here is a simple, progressive routine you can follow safely.\n"
        "* The idea is to move regularly, build basic strength and support it with good nutrition and recovery habits.\n\n"
        "**Training plan (3 sessions per week max)**\n"
        "* Monday: 30–40 minutes of brisk walking or easy cycling, followed by 5–10 minutes of light stretching.\n"
        "* Wednesday: 30 minutes of body-weight strength (squats, lunges, push-ups against a wall or on knees, plank 3×20–30 s).\n"
        "* Friday: 30–40 minutes of cardio of your choice (incline walk, bike, easy swimming or a dynamic yoga session) + deep breathing.\n"
        "* Optional: on the weekend, 10–15 minutes of mobility and gentle stretching to relax your body.\n\n"
        "**Nutrition and hydration tips**\n"
        "* Drink water regularly throughout the day (around 6–8 glasses) and around your workouts.\n"
        "* Build your meals around: a source of protein (eggs, fish, legumes, tofu), plenty of vegetables and a complex carb (brown rice, quinoa, oats, whole-grain bread).\n"
        "* Limit highly processed foods, sugary drinks and fast-food to occasional treats.\n"
        "* Choose simple snacks: fresh fruit, plain yogurt, a handful of nuts.\n"
        "* Try to keep fairly regular meal times to stabilise your energy.\n\n"
        "**Recovery / sleep / motivation tips**\n"
        "* Aim for 7–8 hours of sleep per night in a dark, quiet room, and avoid screens just before bed.\n"
        "* After each session, take a few minutes to stretch and breathe deeply to let your muscles and mind relax.\n"
        "* Listen to your body: if you feel unusual pain, reduce intensity or swap the exercise for a gentler option.\n"
        "* Set small, realistic goals (for example: walk 3 times per week for a month) and track your progress.\n"
        "* If you have a medical condition or persistent pain, ask advice from a health professional.\n"
    )


# -------------------------------------------------------
# Llamada al modelo IA en HuggingFace Router
# -------------------------------------------------------
async def call_huggingface(question: str, lang: str, history: Optional[list] = None) -> str:
    if not HF_API_TOKEN:
        return ""

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    # ---- Construir a conversa completa ----
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Histórico vindo do frontend: [{ id, role, text }, ...]
    if history:
        # pegamos só as últimas 8 mensagens para não explodir tokens
        for item in history[-8:]:
            role = "assistant" if (item.get("role") == "assistant") else "user"
            text = (item.get("text") or "").strip()
            if not text:
                continue
            messages.append({"role": role, "content": text})

    # Mensagem atual do usuário (última pergunta)
    messages.append({
        "role": "user",
        "content": f"Langue de l'utilisateur: {lang}\nDernier message: {question}"
    })

    payload = {
        "model": HF_MODEL,
        "messages": messages,
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

   # --- Llamar al modelo HF (con historial) ---
    answer = await call_huggingface(msg, lang, req.history)

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
