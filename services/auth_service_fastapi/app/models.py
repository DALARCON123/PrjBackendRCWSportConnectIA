# -------------------------------------------------------
# Importations nécessaires de SQLAlchemy :
# - Column : pour définir les colonnes
# - Integer, String, DateTime : types de données SQL
# - func : permet d'utiliser des fonctions SQL (comme NOW())
# -------------------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime, func

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

    # ---------------------------------------------------
    # Nom de la table dans la base : "users"
    # ---------------------------------------------------
    __tablename__ = "users"

    # ---------------------------------------------------
    # Colonne 'id' : identifiant unique, clé primaire
    # index=True : crée un index pour accélérer les requêtes
    # ---------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ---------------------------------------------------
    # Colonne 'name' : nom de l'utilisateur
    # nullable=True : optionnel
    # ---------------------------------------------------
    name = Column(String(200), nullable=True)

    # ---------------------------------------------------
    # Colonne 'email' : adresse électronique (unique)
    # unique=True : empêche les doublons
    # index=True : accélère la recherche par email
    # nullable=False : obligatoire
    # ---------------------------------------------------
    email = Column(String(320), unique=True, index=True, nullable=False)

    # ---------------------------------------------------
    # Colonne 'password_hash' : mot de passe chiffré
    # nullable=False : obligatoire
    # ---------------------------------------------------
    password_hash = Column(String(255), nullable=False)

    # ---------------------------------------------------
    # Colonne 'created_at' : date de création automatique
    # server_default=func.now() : la BD remplit la date
    # ---------------------------------------------------
    created_at = Column(DateTime, server_default=func.now())
