from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Date
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# -------------------------------------------------------
# Base SQLAlchemy para declarar los modelos
# -------------------------------------------------------
Base = declarative_base()


# =======================================================
#                 Modèle : User
# Représente un utilisateur du Coach IA
# =======================================================
class User(Base):
    __tablename__ = "coach_users"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(128), unique=True, index=True)  # email/id du frontend
    profile = Column(Text, default="{}")                        # profil JSON

    # Relations avec interactions, plans et logs alimentaires
    interactions = relationship("Interaction", back_populates="user", cascade="all,delete")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all,delete")
    meal_logs = relationship("MealLog", back_populates="user", cascade="all,delete")


# =======================================================
#                 Modèle : Interaction
# Historique des questions/réponses du coach IA
# =======================================================
class Interaction(Base):
    __tablename__ = "coach_interactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("coach_users.id"))
    kind = Column(String(32), default="chat")       # type : chat / sport / nutrition
    question = Column(Text)                         # question du user
    answer = Column(Text)                           # réponse du coach IA
    extracted = Column(Text, default="{}")          # infos extraídas (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interactions")


# =======================================================
#                 Modèle : MealPlan
# Plan alimentaire hebdomadaire généré pour un user
# =======================================================
class MealPlan(Base):
    __tablename__ = "coach_meal_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("coach_users.id"))
    week = Column(String(16))                       # ex: "2025-W10"
    summary = Column(Text)                          # résumé du plan
    details = Column(Text)                          # détails jour par jour
    kcal_target = Column(Integer, nullable=True)
    protein_g = Column(Integer, nullable=True)
    carbs_g = Column(Integer, nullable=True)
    fat_g = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meal_plans")


# =======================================================
#                 Modèle : MealLog
# Journal alimentaire : repas consommés par jour
# =======================================================
class MealLog(Base):
    __tablename__ = "coach_meal_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("coach_users.id"))
    date = Column(Date, index=True)                 # date du repas
    meal = Column(String(32))                       # breakfast/lunch/dinner/snack
    food = Column(Text)                             # description du repas
    kcal = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meal_logs")
