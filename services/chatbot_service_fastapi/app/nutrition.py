from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date
import os, json, httpx, re

from .db import SessionLocal
from .models import User, Interaction, MealPlan, MealLog

# -------------------------------------------------------
# Router FastAPI pour la partie nutrition
# -------------------------------------------------------
router = APIRouter(prefix="/nutrition", tags=["nutrition"])

# -------------------------------------------------------
# Config OpenAI (clé, URL, modèle, mots-clés nutrition)
# -------------------------------------------------------
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
NUTRITION_KEYS = set(os.getenv("NUTRITION_DOMAINS","nutrition,diet,meal,calorie,protein,carbs,fat,alimentación").split(","))

# -------------------------------------------------------
# Prompt système pour l’assistant de nutrition
# -------------------------------------------------------
SYSTEM = (
"You are NutriCoach, a sports-nutrition assistant. "
"Only discuss athlete nutrition, body recomposition, performance, recovery and healthy habits. "
"If outside nutrition, politely refuse and suggest a nutrition angle. "
"Provide clear quantities (g or household units), kcal and macro estimates, and short rationale. "
"Consider allergies, cultural preferences and budget if present."
)

# -------------------------------------------------------
# Prompt pour extraire un profil nutritionnel en JSON
# -------------------------------------------------------
EXTRACTOR = """Extract nutrition attributes from the last message. Return ONLY JSON:
{
  "allergies": [string],
  "diet_style": [ "omnivorous", "vegetarian", "vegan", "mediterranean", "low_carb", "gluten_free", "lactose_free" ],
  "budget": "low" | "medium" | "high",
  "calorie_target": int,
  "protein_target_g": int,
  "carb_target_g": int,
  "fat_target_g": int,
  "meals_per_day": int,
  "dislikes": [string],
  "cultural": [string]
}
"""

# -------------------------------------------------------
# Vérifie si le texte parle de nutrition sportive
# -------------------------------------------------------
def _is_nutrition(text:str)->bool:
    t=text.lower()
    return any(k.strip() in t for k in NUTRITION_KEYS) or bool(re.search(r"\b(calor(?:ías|ies)|macro|prote(?:í|i)na|carb|grasa|dieta|men[uú]|comida)\b", t))

# -------------------------------------------------------
# Appel à l’API OpenAI (chat completions)
# -------------------------------------------------------
def _openai(messages, temperature=0.2, max_tokens=1200):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"}
    payload = {"model": MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    with httpx.Client(timeout=60) as c:
        r = c.post(f"{OPENAI_API_BASE}/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

# -------------------------------------------------------
# Modèle d’entrée pour poser une question nutrition
# -------------------------------------------------------
class AskIn(BaseModel):
    user_id: str
    query: str

# -------------------------------------------------------
# Endpoint : /nutrition/ask → réponse de NutriCoach
# -------------------------------------------------------
@router.post("/ask")
def ask(in_: AskIn):
    # Si no es nutrición → mensaje de rechazo
    if not _is_nutrition(in_.query):
        return {"content":"Solo puedo ayudarte con NUTRICIÓN deportiva. Dime objetivos, alergias, presupuesto y preferencia (vegana, mediterránea, etc.)."}

    messages = [{"role":"system","content": SYSTEM}, {"role":"user","content": in_.query}]
    try:
        answer = _openai(messages)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"OpenAI error: {e}")

    # --- extracción de atributos en JSON ---
    bits = {}
    try:
        js = _openai([
            {"role":"system","content":"Return strict JSON only."},
            {"role":"user","content": EXTRACTOR + "\n---\n" + in_.query}
        ], temperature=0.0, max_tokens=400)
        bits = json.loads(js)
    except Exception:
        bits = {}

    # --- guardar en BD : user, perfil y interacción ---
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.external_id==in_.user_id)).scalar_one_or_none()
        if not u:
            u = User(external_id=in_.user_id, profile="{}"); db.add(u); db.flush()

        # fusion du profil existant avec les nouveaux datos
        try: base = json.loads(u.profile) if u.profile else {}
        except: base = {}
        for k,v in (bits or {}).items():
            if v in [None,"",[],{}]: continue
            if isinstance(v,list):
                base[k]=sorted(list(set((base.get(k,[]) or [])+v)))
            else:
                base[k]=v
        u.profile = json.dumps(base, ensure_ascii=False)

        inter = Interaction(
            user_id=u.id,
            kind="nutrition",
            question=in_.query,
            answer=answer,
            extracted=json.dumps(bits, ensure_ascii=False)
        )
        db.add(inter); db.commit()

    return {"content": answer, "extracted": bits}

# -------------------------------------------------------
# Modèle d’entrée para pedir un plan semanal
# -------------------------------------------------------
class PlanIn(BaseModel):
    user_id: str
    week: str | None = None

# -------------------------------------------------------
# Endpoint : /nutrition/plan → genera plan 7 días
# -------------------------------------------------------
@router.post("/plan")
def plan(in_: PlanIn):
    # semana tipo "2025-W10" si no viene
    w = in_.week or f"{date.today().isocalendar().year}-W{date.today().isocalendar().week:02d}"
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.external_id==in_.user_id)).scalar_one_or_none()
        if not u: raise HTTPException(404, "user not found")

        profile = u.profile or "{}"
        prompt = (
            "Create a 7-day athlete nutrition plan from this JSON profile:\n"
            f"{profile}\n\nRules:\n"
            "- Sports-only nutrition focus.\n"
            "- Show kcal & macros per day (protein/carbs/fat grams).\n"
            "- 3–5 meals/day with quantities.\n"
            "- Consider allergies, diet style, dislikes, cultural prefs and budget.\n"
            "- Add grocery list and prep tips.\n"
            "- Output in concise Markdown with tables where useful."
        )
        plan_md = _openai(
            [{"role":"system","content": SYSTEM},{"role":"user","content": prompt}],
            temperature=0.2,
            max_tokens=1600
        )

        # intento simple de extraer un valor kcal del texto
        kcal=None
        try:
            m=re.search(r"(\d{3,5})\s*kcal", plan_md.lower()); kcal=int(m.group(1)) if m else None
        except: pass

        p = MealPlan(
            user_id=u.id,
            week=w,
            summary=f"Plan nutricional {w}",
            details=plan_md,
            kcal_target=kcal
        )
        db.add(p); db.commit()
        return {"week": w, "plan": plan_md}

# -------------------------------------------------------
# Modèle d’entrée pour enregistrer un repas
# -------------------------------------------------------
class LogIn(BaseModel):
    user_id: str
    date: date
    meal: str
    food: str
    kcal: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    notes: str | None = ""

# -------------------------------------------------------
# Endpoint : /nutrition/log → guardar un registro de comida
# -------------------------------------------------------
@router.post("/log")
def log_meal(in_: LogIn):
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.external_id==in_.user_id)).scalar_one_or_none()
        if not u: raise HTTPException(404, "user not found")
        entry = MealLog(
            user_id=u.id,
            date=in_.date,
            meal=in_.meal,
            food=in_.food,
            kcal=in_.kcal,
            protein_g=in_.protein_g,
            carbs_g=in_.carbs_g,
            fat_g=in_.fat_g,
            notes=in_.notes or ""
        )
        db.add(entry); db.commit()
    return {"ok": True}
