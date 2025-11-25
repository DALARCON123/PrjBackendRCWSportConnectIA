# -------------------------------------------------------
# Importation de Pydantic :
# - BaseModel : base pour créer des modèles de validation
# - EmailStr : type spécial pour valider automatiquement les emails
# -------------------------------------------------------
from pydantic import BaseModel, EmailStr

# -------------------------------------------------------
# Autres types utiles :
# - Optional : pour les champs facultatifs
# - datetime : pour les dates de création
# -------------------------------------------------------
from typing import Optional
from datetime import datetime


# =======================================================
# Modèle Pydantic : RegisterDto
# Utilisé lors de l'inscription d'un nouvel utilisateur
# =======================================================
class RegisterDto(BaseModel):
    # Nom de l'utilisateur (optionnel)
    name: Optional[str] = None

    # Adresse email (validée automatiquement)
    email: EmailStr

    # Mot de passe non chiffré envoyé par l'utilisateur
    password: str


# =======================================================
# Modèle Pydantic : LoginDto
# Utilisé lors de la connexion (login)
# =======================================================
class LoginDto(BaseModel):
    # Email obligatoire, validé automatiquement
    email: EmailStr

    # Mot de passe fourni par l'utilisateur pour la connexion
    password: str


# =======================================================
# Modèle Pydantic : TokenOut
# Réponse envoyée après un login réussi
# Contient le jeton JWT
# =======================================================
class TokenOut(BaseModel):
    # access_token : le token JWT généré
    access_token: str

    # type du token, ici toujours "Bearer"
    token_type: str = "Bearer"


# =======================================================
# Modèle Pydantic : UserOut
# Utilisé pour renvoyer les infos d'un utilisateur
# (profil, liste des utilisateurs pour l'admin, etc.)
# =======================================================
class UserOut(BaseModel):
    # Identifiant unique
    id: int

    # Nom complet (optionnel)
    name: Optional[str] = None

    # Email de l'utilisateur
    email: EmailStr

    # L'utilisateur est-il actif ?
    is_active: bool

    # L'utilisateur est-il administrateur ?
    is_admin: bool

    # Date de création du compte
    created_at: datetime


# =======================================================
# Modèle Pydantic : AdminUpdateUser
# Utilisé par l'administrateur pour modifier un utilisateur
# (nom, email, mot de passe, statut actif, rôle admin, etc.)
# =======================================================
class AdminUpdateUser(BaseModel):
    # Nouveau nom (optionnel)
    name: Optional[str] = None

    # Nouvel email (optionnel)
    email: Optional[EmailStr] = None

    # Nouveau mot de passe (optionnel)
    # ⚠ Ce mot de passe sera chiffré côté backend
    new_password: Optional[str] = None

    # Activer / désactiver le compte
    is_active: Optional[bool] = None

    # Donner / retirer le rôle administrateur
    is_admin: Optional[bool] = None


# =======================================================
# Modèles pour les notifications envoyées par l'admin
# =======================================================
class NotificationCreate(BaseModel):
    # ID de l'utilisateur ciblé
    user_id: int

    # Titre de la notification
    title: str

    # Message à envoyer
    message: str


class NotificationOut(BaseModel):
    # Identifiant de la notification
    id: int

    # ID de l'utilisateur concerné
    user_id: int

    # Titre + message
    title: str
    message: str

    # Statut de lecture
    is_read: bool

    # Date d'envoi
    created_at: datetime
