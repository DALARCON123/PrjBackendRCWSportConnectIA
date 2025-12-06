# app/security.py

# -------------------------------------------------------
# Imports : bcrypt pour hacher, jwt pour tokens, datetime, os
# -------------------------------------------------------
import bcrypt
import jwt
import datetime
import os

# -------------------------------------------------------
# Imports FastAPI / SQLAlchemy pour la gestion des utilisateurs
# -------------------------------------------------------
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .models import User
from .db import get_db

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
        "exp": now + datetime.timedelta(minutes=ACCESS_MIN),
        "iss": os.getenv("APP_NAME", "AuthService"),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


# -------------------------------------------------------
# Décoder un JWT pour extraire les informations
# -------------------------------------------------------
def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception:
        return None


# -------------------------------------------------------
# Récupérer l'utilisateur actuel via le token Authorization
# -------------------------------------------------------
def get_current_user(
    token: str = Depends(lambda authorization=Depends(lambda request=None: None): 
                         authorization)
):
    """
    Cette fonction sera remplacée dans main.py via un Depends(get_current_user_from_token)
    car FastAPI ne permet pas directement de lire le header ici.
    Je la laisse simple pour structure.
    """
    return None


# -------------------------------------------------------
# Fonction réelle pour extraire l'utilisateur depuis le token
# (appelée depuis main.py grâce à Header)
# -------------------------------------------------------
def get_current_user_from_token(token: str, db: Session):
    data = decode_jwt(token)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré.",
        )

    user = db.query(User).filter(User.id == int(data["sub"])).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )

    return user


# -------------------------------------------------------
# Vérifier si l'utilisateur actuel est actif
# -------------------------------------------------------
def get_current_active_user(
    token: str,
    db: Session = Depends(get_db),
):
    user = get_current_user_from_token(token, db)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est désactivé.",
        )

    return user


# -------------------------------------------------------
# Vérifier si l'utilisateur actuel est administrateur
# -------------------------------------------------------
def get_current_admin(
    token: str,
    db: Session = Depends(get_db),
):
    user = get_current_user_from_token(token, db)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : administrateur requis.",
        )

    return user
