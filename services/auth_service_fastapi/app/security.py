# app/security.py
import bcrypt
import jwt
import datetime
import os

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def generate_jwt(sub: str, email: str, name: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": sub,
        "email": email,
        "name": name,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=ACCESS_MIN),
        "iss": os.getenv("APP_NAME", "AuthService"),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
