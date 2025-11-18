# services/auth_service_fastapi/app/main.py

# -------------------------------------------------------
# Importations nécessaires pour FastAPI et gestion d’erreurs
# -------------------------------------------------------
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------------------------------
# Pydantic : modèles de validation pour les requêtes entrantes
# -------------------------------------------------------
from pydantic import BaseModel

# -------------------------------------------------------
# dotenv pour charger les variables d’environnement depuis un fichier .env
# -------------------------------------------------------
from dotenv import load_dotenv

# -------------------------------------------------------
# Path pour manipuler les chemins de fichiers de façon portable
# os pour lire les variables d’environnement
# -------------------------------------------------------
from pathlib import Path
import os


# =======================================================
# Chargement du fichier .env situé à la racine du projet
# Exemple : .../PrjBackendRCWSportConnectIA/.env
# =======================================================
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)


# -------------------------------------------------------
# Importation des fonctions de sécurité :
# - hash_password : hachage du mot de passe
# - verify_password : vérification du mot de passe
# - generate_jwt : création d’un jeton JWT
# -------------------------------------------------------
from .security import hash_password, verify_password, generate_jwt


# =======================================================
# Lecture du port dans les variables d’environnement
# Priorité : AUTH_PORT → PORT → valeur par défaut 8001
# =======================================================
AUTH_PORT = int(os.getenv("AUTH_PORT") or os.getenv("PORT", "8001"))


# -------------------------------------------------------
# Création de l’application FastAPI dédiée au service Auth
# -------------------------------------------------------
app = FastAPI(title="Auth Service")


# =======================================================
# Configuration du CORS pour autoriser les requêtes du frontend Vite
# Ces URLs correspondent aux environnements locaux de développement
# =======================================================
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


# =======================================================
#               MODÈLES Pydantic (DTO)
# =======================================================

# -------------------------------------------------------
# Modèle pour l’enregistrement d’un utilisateur
# -------------------------------------------------------
class RegisterIn(BaseModel):
    email: str
    password: str
    name: str | None = ""


# -------------------------------------------------------
# Modèle pour la connexion (login)
# -------------------------------------------------------
class LoginIn(BaseModel):
    email: str
    password: str


# -------------------------------------------------------
# Modèle de réponse lors de la génération du token JWT
# -------------------------------------------------------
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"


# =======================================================
# Base de données temporaire en mémoire (dictionnaire Python)
# Utilisée uniquement pour tests rapides
# =======================================================
USERS: dict[str, dict] = {}


# =======================================================
#                   ENDPOINTS API
# =======================================================

# -------------------------------------------------------
# Route de santé pour vérifier que le service Auth fonctionne
# -------------------------------------------------------
@app.get("/auth/health")
def health():
    return {"status": "ok", "service": "auth"}


# -------------------------------------------------------
# Endpoint d’inscription d’un utilisateur
# Vérifie :
# - email et mot de passe présents
# - utilisateur déjà existant ou non
# Enregistre l’utilisateur dans USERS avec son mot de passe haché
# -------------------------------------------------------
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


# -------------------------------------------------------
# Endpoint de connexion (login)
# Vérifie :
# - que l’utilisateur existe
# - que le mot de passe est correct
# Retourne un JWT si authentification valide
# -------------------------------------------------------
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


# =======================================================
# Permet d'exécuter ce service directement avec :
# python app/main.py
# (Uvicorn se lance automatiquement)
# =======================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=AUTH_PORT, reload=True)
