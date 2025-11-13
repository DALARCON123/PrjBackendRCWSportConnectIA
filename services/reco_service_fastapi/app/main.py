# services/reco_service_fastapi/app/main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from .tracking_db import init_db, get_conn  # 👈 nuevo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Inicializar BD al arrancar ===
@app.on_event("startup")
def bootstrap():
    init_db()

# ====== (ya tenías tus endpoints de /reco/personalized, etc.) ======

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

# ------------ ENDPOINTS TRACKING ------------
@app.get("/tracking/measurements", response_model=List[MeasurementOut])
def get_measurements(email: str = Query(...)):
    with get_conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT id, date, weight_kg, waist_cm, hips_cm, chest_cm, notes
            FROM measurements
            WHERE email=?
            ORDER BY date DESC, id DESC
        """, (email.lower(),))
        rows = [dict(r) for r in cur.fetchall()]
    return rows

@app.post("/tracking/measurements", response_model=dict)
def add_measurement(email: str, body: MeasurementIn):
    if not body.date:
        raise HTTPException(status_code=400, detail="date is required")

    with get_conn() as c:
        cur = c.cursor()
        cur.execute("""
            INSERT INTO measurements(email, date, weight_kg, waist_cm, hips_cm, chest_cm, notes)
            VALUES(?,?,?,?,?,?,?)
        """, (
            email.lower(), body.date, body.weight_kg, body.waist_cm,
            body.hips_cm, body.chest_cm, body.notes
        ))
        c.commit()
        new_id = cur.lastrowid

    return {"ok": True, "id": new_id}
