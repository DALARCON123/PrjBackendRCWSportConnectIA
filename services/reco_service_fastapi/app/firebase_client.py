from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# -------------------------------------------------------
# Chemin vers le dossier du service (racine du module)
# -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]  # .../reco_service_fastapi

# -------------------------------------------------------
# Chemin du fichier de clé Firebase Admin
# -------------------------------------------------------
CRED_PATH = BASE_DIR / "firebase-admin-key.json"

# -------------------------------------------------------
# Initialisation de Firebase avec les identifiants du service
# -------------------------------------------------------
cred = credentials.Certificate(str(CRED_PATH))
firebase_admin.initialize_app(cred)

# -------------------------------------------------------
# Client Firestore pour lire/écrire dans la base
# -------------------------------------------------------
db = firestore.client()

# -------------------------------------------------------
# Raccourci pour utiliser SERVER_TIMESTAMP, Query, etc.
# -------------------------------------------------------
fb_firestore = firestore
