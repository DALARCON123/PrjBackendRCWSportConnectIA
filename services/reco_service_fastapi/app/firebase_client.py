from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = Path(__file__).resolve().parents[1]  # .../reco_service_fastapi
CRED_PATH = BASE_DIR / "firebase-admin-key.json"

cred = credentials.Certificate(str(CRED_PATH))
firebase_admin.initialize_app(cred)

db = firestore.client()
fb_firestore = firestore  # para usar SERVER_TIMESTAMP, Query, etc.
