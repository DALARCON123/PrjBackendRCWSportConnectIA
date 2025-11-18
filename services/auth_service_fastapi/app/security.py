# app/security.py

# -------------------------------------------------------
# Imports : bcrypt pour hacher, jwt pour tokens, datetime, os
# -------------------------------------------------------
import bcrypt
import jwt
import datetime
import os

# -------------------------------------------------------
# Variables du JWT (clé secrète, algorithme, durée)
# -------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# -------------------------------------------------------
# Hachage du mot de passe (bcrypt)
# -------------------------------------------------------
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# -------------------------------------------------------
# Vérifie si un mot de passe correspond au hachage
# -------------------------------------------------------
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# -------------------------------------------------------
# Génère un token JWT contenant infos + expiration
# -------------------------------------------------------
def generate_jwt(sub: str, email: str, name: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": sub,                        # identifiant utilisateur
        "email": email,                    # email
        "name": name,                      # nom
        "iat": now,                        # date de création
        "exp": now + datetime.timedelta(minutes=ACCESS_MIN),  # expiration
        "iss": os.getenv("APP_NAME", "AuthService"),          # émetteur
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
