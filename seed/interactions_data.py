"""
Données mockées pour les interactions avec le coach IA (Chatbot Service)
"""
from datetime import datetime
import json

INTERACTIONS_DATA = [
    {
        "id": 1,
        "user_id": 1,
        "kind": "chat",
        "question": "Comment puis-je perdre du poids de manière saine ?",
        "answer": "Pour une perte de poids saine, je recommande : 1) Un déficit calorique modéré (300-500 kcal/jour), 2) Une alimentation équilibrée riche en légumes, protéines maigres et grains entiers, 3) Une activité physique régulière (3-5 séances/semaine), 4) Un sommeil de qualité (7-9h/nuit). Fixez-vous des objectifs réalistes : 0.5-1 kg par semaine maximum.",
        "extracted": json.dumps({"topic": "weight_loss", "confidence": 0.95}),
        "created_at": datetime(2024, 11, 1, 10, 0, 0)
    },
    {
        "id": 2,
        "user_id": 1,
        "kind": "nutrition",
        "question": "Quel type de petit-déjeuner recommandes-tu pour perdre du poids ?",
        "answer": "Pour un petit-déjeuner équilibré favorisant la perte de poids : Flocons d'avoine (50g) avec fruits rouges, 1 œuf dur, thé vert. Alternative : Yaourt grec nature, granola maison sans sucre, pomme. L'important : protéines (satiété) + fibres (digestion lente) + hydratation.",
        "extracted": json.dumps({"meal": "breakfast", "goal": "weight_loss", "kcal_estimate": 350}),
        "created_at": datetime(2024, 11, 5, 8, 30, 0)
    },
    {
        "id": 3,
        "user_id": 2,
        "kind": "sport",
        "question": "Quel programme d'entraînement pour prendre de la masse musculaire ?",
        "answer": "Programme musculation 4 jours/semaine : Jour 1: Pectoraux/Triceps, Jour 2: Dos/Biceps, Jour 3: Repos, Jour 4: Jambes/Fessiers, Jour 5: Épaules/Abdos, Jour 6-7: Repos. 3-4 séries de 8-12 répétitions par exercice. Charge progressive. Repos 48h entre groupes musculaires. Nutrition : 1.8-2.2g protéines/kg poids corporel.",
        "extracted": json.dumps({"program_type": "strength", "frequency": 4, "duration_weeks": 8}),
        "created_at": datetime(2024, 11, 10, 14, 15, 0)
    },
    {
        "id": 4,
        "user_id": 3,
        "kind": "nutrition",
        "question": "Des idées de repas vegan riches en protéines ?",
        "answer": "Voici des sources de protéines végétales : Tofu grillé (15g/100g), Lentilles (18g/100g cuites), Quinoa (14g/100g cuit), Pois chiches rôtis (19g/100g), Tempeh (19g/100g), Edamame (11g/100g). Idée repas : Bowl Buddha avec quinoa, pois chiches rôtis, légumes grillés, avocat, sauce tahini.",
        "extracted": json.dumps({"dietary_preference": "vegan", "nutrient_focus": "protein"}),
        "created_at": datetime(2024, 11, 12, 12, 45, 0)
    },
    {
        "id": 5,
        "user_id": 4,
        "kind": "sport",
        "question": "Comment améliorer mon endurance pour un marathon ?",
        "answer": "Plan d'entraînement marathon (12 semaines) : Semaines 1-4: Base aérobie (3-4 sorties courtes 5-8km), Semaines 5-8: Volume croissant (sortie longue hebdo jusqu'à 20km), Semaines 9-11: Pics d'intensité (fractionné + sortie longue 25-32km), Semaine 12: Affûtage (réduction volume). Hydratation cruciale. Récupération active. Échauffement/étirements systématiques.",
        "extracted": json.dumps({"sport": "running", "goal": "marathon", "duration_weeks": 12}),
        "created_at": datetime(2024, 11, 15, 7, 20, 0)
    },
    {
        "id": 6,
        "user_id": 5,
        "kind": "chat",
        "question": "Quels exercices de yoga pour réduire le stress ?",
        "answer": "Séquence anti-stress (20 min) : 1) Respiration profonde (5 min), 2) Posture de l'enfant (3 min), 3) Chat-vache (2 min), 4) Torsion assise (2 min/côté), 5) Pigeon (2 min/côté), 6) Savasana (5 min). Pratiquez le soir, lumière tamisée, musique douce. Focus sur la respiration lente et profonde.",
        "extracted": json.dumps({"activity": "yoga", "goal": "stress_reduction", "duration_minutes": 20}),
        "created_at": datetime(2024, 11, 18, 19, 0, 0)
    },
]
