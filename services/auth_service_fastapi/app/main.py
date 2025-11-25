# services/auth_service_fastapi/app/main.py

# -------------------------------------------------------
# Importations nécessaires pour FastAPI et gestion d’erreurs
# -------------------------------------------------------
from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------------------------------
# Typage pour les réponses listes
# -------------------------------------------------------
from typing import List

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

# =======================================================
# Importation de la couche sécurité (hash / vérification / JWT)
# et des dépendances pour récupérer l'utilisateur courant
# =======================================================
from .security import (
    hash_password,
    verify_password,
    generate_jwt,
    get_current_active_user,
    get_current_admin,
)

# =======================================================
# Importation des modèles SQLAlchemy et de la BD
# =======================================================
from .db import Base, engine, get_db
from .models import User, Notification

# =======================================================
# Importation des schémas Pydantic (DTO)
# =======================================================
from .schemas import (
    RegisterDto,
    LoginDto,
    TokenOut,
    UserOut,
    AdminUpdateUser,
    NotificationCreate,
    NotificationOut,
)

# =======================================================
# Lecture du port dans les variables d’environnement
# Priorité : AUTH_PORT → PORT → valeur par défaut 8001
# =======================================================
AUTH_PORT = int(os.getenv("AUTH_PORT") or os.getenv("PORT", "8001"))

# -------------------------------------------------------
# Création de l’application FastAPI dédiée au service Auth
# -------------------------------------------------------
app = FastAPI(title="Auth Service SportConnectIA")

# -------------------------------------------------------
# Création des tables dans la base de données (si non existantes)
# -------------------------------------------------------
Base.metadata.create_all(bind=engine)

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
#           FONCTIONS UTILITAIRES / DÉPENDANCES
# =======================================================

# -------------------------------------------------------
# Récupérer le token Bearer depuis le header Authorization
# Exemple : "Authorization: Bearer xxxxx"
# -------------------------------------------------------
def get_token_from_header(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization invalide.",
        )
    return authorization.split(" ", 1)[1]


# -------------------------------------------------------
# Récupérer l'utilisateur courant (actif) à partir du token
# -------------------------------------------------------
def get_current_user_dep(
    token: str = Depends(get_token_from_header),
    db=Depends(get_db),
) -> User:
    return get_current_active_user(token, db)


# -------------------------------------------------------
# Récupérer l'administrateur courant à partir du token
# -------------------------------------------------------
def get_current_admin_dep(
    token: str = Depends(get_token_from_header),
    db=Depends(get_db),
) -> User:
    return get_current_admin(token, db)


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
# Utilise la vraie base de données (table users)
# -------------------------------------------------------
@app.post("/auth/register", status_code=201)
def register(body: RegisterDto, db=Depends(get_db)):
    email = body.email.lower().strip()

    if not email or not body.password:
        raise HTTPException(status_code=400, detail="email and password are required")

    # Vérifier si l'utilisateur existe déjà
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="user already exists")

    # Créer un nouvel utilisateur
    new_user = User(
        name=body.name or "",
        email=email,
        password_hash=hash_password(body.password),
        is_active=True,
        is_admin=False,  # Par défaut, un nouvel utilisateur n'est pas admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"email": new_user.email, "id": new_user.id}


# -------------------------------------------------------
# Endpoint de connexion (login)
# Retourne un JWT si authentification valide
# -------------------------------------------------------
@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginDto, db=Depends(get_db)):
    email = body.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    # sub = id de l'utilisateur (en string)
    token = generate_jwt(str(user.id), user.email, user.name or "")

    return TokenOut(access_token=token, token_type="Bearer")


# -------------------------------------------------------
# Endpoint : profil de l'utilisateur courant (token requis)
# -------------------------------------------------------
@app.get("/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user_dep)):
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )


# =======================================================
#           ENDPOINTS ADMIN : GESTION UTILISATEURS
# =======================================================

# -------------------------------------------------------
# Liste de tous les utilisateurs (admin seulement)
# -------------------------------------------------------
@app.get(
    "/auth/admin/users",
    response_model=List[UserOut],
    summary="Lister tous les utilisateurs (admin)",
)
def admin_list_users(
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_dep),
):
    users = db.query(User).all()
    return [
        UserOut(
            id=u.id,
            name=u.name,
            email=u.email,
            is_active=u.is_active,
            is_admin=u.is_admin,
            created_at=u.created_at,
        )
        for u in users
    ]


# -------------------------------------------------------
# Obtenir un utilisateur par ID (admin seulement)
# -------------------------------------------------------
@app.get(
    "/auth/admin/users/{user_id}",
    response_model=UserOut,
    summary="Obtenir un utilisateur (admin)",
)
def admin_get_user(
    user_id: int,
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_dep),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="user not found")

    return UserOut(
        id=u.id,
        name=u.name,
        email=u.email,
        is_active=u.is_active,
        is_admin=u.is_admin,
        created_at=u.created_at,
    )


# -------------------------------------------------------
# Modifier un utilisateur (admin : nom, email, actif, admin, mot de passe)
# -------------------------------------------------------
@app.put(
    "/auth/admin/users/{user_id}",
    response_model=UserOut,
    summary="Modifier un utilisateur (admin)",
)
def admin_update_user(
    user_id: int,
    body: AdminUpdateUser,
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_dep),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="user not found")

    if body.name is not None:
        u.name = body.name

    if body.email is not None:
        # Vérifier si un autre utilisateur a déjà cet email
        existing = (
            db.query(User)
            .filter(User.email == body.email, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="email already in use")
        u.email = body.email.lower().strip()

    if body.is_active is not None:
        u.is_active = body.is_active

    if body.is_admin is not None:
        u.is_admin = body.is_admin

    if body.new_password:
        u.password_hash = hash_password(body.new_password)

    db.add(u)
    db.commit()
    db.refresh(u)

    return UserOut(
        id=u.id,
        name=u.name,
        email=u.email,
        is_active=u.is_active,
        is_admin=u.is_admin,
        created_at=u.created_at,
    )


# =======================================================
#     ENDPOINTS NOTIFICATIONS (ADMIN → UTILISATEUR)
# =======================================================

# -------------------------------------------------------
# Envoyer une notification à un utilisateur (admin seulement)
# -------------------------------------------------------
@app.post(
    "/auth/admin/notifications",
    response_model=NotificationOut,
    summary="Envoyer une notification à un utilisateur (admin)",
)
def admin_send_notification(
    body: NotificationCreate,
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_dep),
):
    # Vérifier que l'utilisateur ciblé existe
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    notif = Notification(
        user_id=body.user_id,
        title=body.title,
        message=body.message,
    )

    db.add(notif)
    db.commit()
    db.refresh(notif)

    return NotificationOut(
        id=notif.id,
        user_id=notif.user_id,
        title=notif.title,
        message=notif.message,
        is_read=notif.is_read,
        created_at=notif.created_at,
    )


# -------------------------------------------------------
# Lister les notifications de l'utilisateur courant
# -------------------------------------------------------
@app.get(
    "/auth/me/notifications",
    response_model=List[NotificationOut],
    summary="Lister mes notifications",
)
def get_my_notifications(
    db=Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return [
        NotificationOut(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifs
    ]


# =======================================================
# Permet d'exécuter ce service directement avec :
# python app/main.py
# (Uvicorn se lance automatiquement)
# =======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=AUTH_PORT, reload=True)
