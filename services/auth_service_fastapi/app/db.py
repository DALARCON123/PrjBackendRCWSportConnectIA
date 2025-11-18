# -------------------------------------------------------
# Importation du module sqlite3 pour gérer la base SQLite
# -------------------------------------------------------
import sqlite3

# -------------------------------------------------------
# Importation de Path pour construire des chemins dynamiques
# -------------------------------------------------------
from pathlib import Path

# -------------------------------------------------------
# Définition du chemin complet vers la base de données "auth.db"
# Le fichier se trouve deux niveaux au-dessus du script actuel
# -------------------------------------------------------
DB_PATH = Path(__file__).resolve().parent.parent / "auth.db"


# -------------------------------------------------------
# Fonction pour obtenir une connexion active à la base SQLite
# row_factory permet d'accéder aux colonnes par leur nom
# -------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------------
# Fonction d'initialisation de la base de données
# Elle crée la table 'users' si elle n'existe pas déjà
# Les colonnes :
#   - email : identifiant principal (clé primaire)
#   - name : nom de l'utilisateur
#   - password_hash : mot de passe chiffré
#   - created_at : date et heure d'inscription (automatique)
# -------------------------------------------------------
def init_db():
    with get_conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
