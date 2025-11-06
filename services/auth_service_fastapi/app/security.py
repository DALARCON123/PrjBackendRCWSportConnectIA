import os, datetime, jwt
from passlib.context import CryptContext

JWT_SECRET = os.getenv("JWT_SECRET", "changeme-super-secret")
JWT_ISSUER = os.getenv("JWT_ISSUER", "rcw.sport")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "rcw.sport.clients")
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "4"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

def generate_jwt(sub: str, email: str, name: str | None) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + datetime.timedelta(hours=JWT_EXPIRES_HOURS),
        "sub": sub,
        "email": email,
        "name": name or "",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
