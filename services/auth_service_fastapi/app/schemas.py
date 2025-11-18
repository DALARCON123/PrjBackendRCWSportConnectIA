# -------------------------------------------------------
# Importation de Pydantic :
# - BaseModel : base pour créer des modèles de validation
# - EmailStr : type spécial pour valider automatiquement les emails
# -------------------------------------------------------
from pydantic import BaseModel, EmailStr


# =======================================================
# Modèle Pydantic : RegisterDto
# Utilisé lors de l'inscription d'un nouvel utilisateur
# =======================================================
class RegisterDto(BaseModel):
    # ---------------------------------------------------
    # 'name' : nom de l'utilisateur (optionnel)
    # None = valeur par défaut si non fourni
    # ---------------------------------------------------
    name: str | None = None

    # ---------------------------------------------------
    # 'email' : adresse email (validée automatiquement)
    # EmailStr vérifie le format correct (ex: test@mail.com)
    # ---------------------------------------------------
    email: EmailStr

    # ---------------------------------------------------
    # 'password' : mot de passe non chiffré envoyé par l'utilisateur
    # ---------------------------------------------------
    password: str


# =======================================================
# Modèle Pydantic : LoginDto
# Utilisé lors de la connexion (login)
# =======================================================
class LoginDto(BaseModel):
    # ---------------------------------------------------
    # Email obligatoire, validé automatiquement
    # ---------------------------------------------------
    email: EmailStr

    # ---------------------------------------------------
    # Mot de passe fourni par l'utilisateur pour la connexion
    # ---------------------------------------------------
    password: str


# =======================================================
# Modèle Pydantic : TokenOut
# Réponse envoyée après un login réussi
# Contient le jeton JWT
# =======================================================
class TokenOut(BaseModel):
    # ---------------------------------------------------
    # access_token : le token JWT généré
    # ---------------------------------------------------
    access_token: str

    # ---------------------------------------------------
    # type du token, ici toujours "Bearer"
    # ---------------------------------------------------
    token_type: str = "Bearer"
