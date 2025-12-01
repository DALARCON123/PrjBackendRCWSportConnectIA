"""
MongoDB Client Configuration
Connexion avec MongoDB pour stocker les données des capteurs et les métriques de santé.
"""

from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
import os

# -------------------------------------------------------
# Charger les variables d'environnement depuis le fichier .env
# -------------------------------------------------------
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# -------------------------------------------------------
# Configuration de MongoDB
# -------------------------------------------------------
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "RCW")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI non trouvée dans le fichier .env")

# -------------------------------------------------------
# Cliente MongoDB
# -------------------------------------------------------
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]

# -------------------------------------------------------
# Collections principais
# -------------------------------------------------------
users_collection = db["users"]
recommendations_collection = db["recommendations"]
sensor_data_collection = db["sensor_data"]
health_metrics_collection = db["health_metrics"]

print(f"[MongoDB] Conectado ao banco: {MONGODB_DB_NAME}")
