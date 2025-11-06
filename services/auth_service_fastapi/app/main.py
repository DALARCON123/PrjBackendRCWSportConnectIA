from fastapi import FastAPI, HTTPException, status
from app.security import generate_jwt, hash_password, verify_password
from app.schemas import RegisterDto, LoginDto, TokenOut

app = FastAPI()

# "banco" em memória para testes
USERS: dict[str, dict] = {}

@app.get("/auth/health")
def health():
    return {"status": "ok", "service": "auth"}

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterDto):
    email = data.email.lower()
    if email in USERS:
        raise HTTPException(status_code=409, detail="email already registered")
    USERS[email] = {
        "name": data.name or "",
        "email": email,
        "password_hash": hash_password(data.password),
    }
    return {"email": email, "name": USERS[email]["name"]}

@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginDto):
    email = data.email.lower()
    user = USERS.get(email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = generate_jwt(sub=email, email=email, name=user["name"])
    return {"access_token": token, "token_type": "Bearer"}
