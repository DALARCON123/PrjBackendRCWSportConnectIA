# app/make_admin.py
# -------------------------------------------------------
# Petit script utilitaire pour transformer un utilisateur
# existant en ADMIN dans la base SQLite auth.db
# -------------------------------------------------------

from app.db import SessionLocal
from app.models import User

# Ouvre une session vers la base de données
db = SessionLocal()

# 🔹 ICI : mets l'ID de l'utilisateur que tu veux rendre admin
# Pour le premier utilisateur créé, c'est généralement 1
user_id = 1

user = db.query(User).filter(User.id == user_id).first()

if not user:
    print(f"Utilisateur avec ID={user_id} introuvable.")
else:
    user.is_admin = True
    db.commit()
    print(f"L'utilisateur {user.email} (ID={user.id}) est maintenant ADMIN ")
