# services/auth_service_fastapi/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

# =========================
#   Cargar .env de la raíz
#   .../PrjBackendRCWSportConnectIA/.env
# =========================
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

from .security import hash_password, verify_password, generate_jwt

# Leer puerto (soporta AUTH_PORT o PORT por si quedó antiguo)
AUTH_PORT = int(os.getenv("AUTH_PORT") or os.getenv("PORT", "8001"))

app = FastAPI(title="Auth Service")

# CORS para tu frontend Vite
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

# =========================
#   MODELOS Pydantic
# =========================
class RegisterIn(BaseModel):
    email: str
    password: str
    name: str | None = ""


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"


# Por ahora base de usuarios en memoria
USERS: dict[str, dict] = {}


# =========================
#   ENDPOINTS
# =========================
@app.get("/auth/health")
def health():
    return {"status": "ok", "service": "auth"}


@app.post("/auth/register")
def register(body: RegisterIn):
    email = body.email.lower().strip()

    if not email or not body.password:
        raise HTTPException(status_code=400, detail="email and password are required")

    if email in USERS:
        raise HTTPException(status_code=409, detail="user already exists")

    USERS[email] = {
        "name": body.name or "",
        "password_hash": hash_password(body.password),
    }

    return {"email": email}


@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn):
    email = body.email.lower().strip()
    user = USERS.get(email)

    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = generate_jwt(email, email, user["name"])
    return {"access_token": token, "token_type": "Bearer"}


# Solo para ejecutar directamente este servicio
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=AUTH_PORT, reload=True)
