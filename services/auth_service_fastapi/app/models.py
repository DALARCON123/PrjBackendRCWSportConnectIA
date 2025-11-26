# -------------------------------------------------------
# Importations nécessaires de SQLAlchemy :
# - Column : pour définir les colonnes
# - Integer, String, DateTime, Boolean, ForeignKey : types de données SQL
# - func : permet d'utiliser des fonctions SQL (comme NOW())
# -------------------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship

# -------------------------------------------------------
# Importation de la classe Base depuis la configuration de la BD
# Base est la classe parent utilisée pour déclarer des modèles
# -------------------------------------------------------
from .db import Base


# =======================================================
#                 Modèle SQLAlchemy : User
# Représente la table "users" dans la base de données
# =======================================================
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Nom de l'utilisateur (optionnel)
    name = Column(String(200), nullable=True)

    # Adresse email (unique et obligatoire)
    email = Column(String(320), unique=True, index=True, nullable=False)

    # Mot de passe chiffré
    password_hash = Column(String(255), nullable=False)

    # Date automatique de création
    created_at = Column(DateTime, server_default=func.now())

    # -------------------------------------------------------
    # Nouveau champ : l'utilisateur est-il actif ?
    # Permet de désactiver un compte sans le supprimer
    # -------------------------------------------------------
    is_active = Column(Boolean, default=True)

    # -------------------------------------------------------
    # Nouveau champ : rôle administrateur
    # Si True → peut gérer les utilisateurs, envoyer notifications, etc.
    # -------------------------------------------------------
    is_admin = Column(Boolean, default=False)

    # -------------------------------------------------------
    # Relation avec les notifications
    # back_populates permet la liaison bidirectionnelle
    # -------------------------------------------------------
    notifications = relationship("Notification", back_populates="user")


# =======================================================
#         Modèle Notification (envoyée par admin)
# =======================================================
class Notification(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # ID de l'utilisateur concerné par la notification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Titre de la notification
    title = Column(String(255), nullable=False)

    # Message envoyé
    message = Column(String(500), nullable=False)

    # Statut (non lu → lu)
    is_read = Column(Boolean, default=False)

    # Date d'envoi
    created_at = Column(DateTime, server_default=func.now())

    # Relation vers User
    user = relationship("User", back_populates="notifications")
