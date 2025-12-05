from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Date
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "coach_users"
    id = Column(Integer, primary_key=True)
    external_id = Column(String(128), unique=True, index=True)   # email/id del front
    profile = Column(Text, default="{}")

    interactions = relationship("Interaction", back_populates="user", cascade="all,delete")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all,delete")
    meal_logs  = relationship("MealLog", back_populates="user", cascade="all,delete")

class Interaction(Base):
    __tablename__ = "coach_interactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("coach_users.id"))
    kind = Column(String(32), default="chat")                    # chat | sport | nutrition
    question = Column(Text)
    answer = Column(Text)
    extracted = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="interactions")

class MealPlan(Base):
    __tablename__ = "coach_meal_plans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("coach_users.id"))
    week = Column(String(16))
    summary = Column(Text)
    details = Column(Text)
    kcal_target = Column(Integer, nullable=True)
    protein_g = Column(Integer, nullable=True)
    carbs_g   = Column(Integer, nullable=True)
    fat_g     = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="meal_plans")

class MealLog(Base):
    __tablename__ = "coach_meal_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("coach_users.id"))
    date = Column(Date, index=True)
    meal = Column(String(32))                                    # breakfast/lunch/dinner/snack
    food = Column(Text)
    kcal = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g   = Column(Float, nullable=True)
    fat_g     = Column(Float, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="meal_logs")
