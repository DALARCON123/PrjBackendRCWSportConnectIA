from flask import Flask, request, jsonify
from app.security import hash_password, verify_password, generate_jwt

app = Flask(__name__)

USERS = {}

@app.get("/auth/health")
def health():
    return {"status": "ok", "service": "auth"}

@app.post("/auth/register")
def register():
    data = request.json
    email = data["email"]
    password = data["password"]
    name = data.get("name", "")

    hashed = hash_password(password)
    
    USERS[email] = {
        "name": data.name or "",
        "email": email,
        "password_hash": hashed,
        "name": name
    }

    return {"email": email}, 201

@app.post("/auth/login")
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    user = USERS.get(email)
    if not user:
        return {"error": "invalid credentials"}, 401
    
    if not verify_password(password, user["password_hash"]):
        return {"error": "invalid credentials"}, 401

    token = generate_jwt(email, email, user["name"])
    return {"access_token": token, "token_type": "Bearer"}
