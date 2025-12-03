"""
Données mockées pour les profils utilisateurs MongoDB (Reco Service)
Stockées dans la collection 'users' de MongoDB
"""
from datetime import datetime

# Ces données seront insérées dans MongoDB
MONGODB_USERS_DATA = [
    {
        "_id": "marie.dubois@example.com",
        "name": "Marie Dubois",
        "age": 35,
        "weightKg": 65.0,
        "heightCm": 165,
        "mainGoal": "Perte de poids",
        "activityLevel": "moderee",
        "lang": "fr",
        "createdAt": datetime(2024, 11, 1, 10, 0, 0),
        "updatedAt": datetime(2024, 11, 29, 15, 30, 0)
    },
    {
        "_id": "jean.martin@example.com",
        "name": "Jean Martin",
        "age": 42,
        "weightKg": 82.5,
        "heightCm": 178,
        "mainGoal": "Gain musculaire",
        "activityLevel": "elevee",
        "lang": "fr",
        "createdAt": datetime(2024, 11, 1, 10, 15, 0),
        "updatedAt": datetime(2024, 11, 29, 16, 0, 0)
    },
    {
        "_id": "sophie.laurent@example.com",
        "name": "Sophie Laurent",
        "age": 28,
        "weightKg": 58.3,
        "heightCm": 160,
        "mainGoal": "Maintien forme",
        "activityLevel": "moderee",
        "lang": "fr",
        "dietaryPreferences": ["vegan"],
        "createdAt": datetime(2024, 11, 1, 10, 30, 0),
        "updatedAt": datetime(2024, 11, 29, 14, 45, 0)
    },
    {
        "_id": "pierre.dupont@example.com",
        "name": "Pierre Dupont",
        "age": 39,
        "weightKg": 75.0,
        "heightCm": 175,
        "mainGoal": "Endurance",
        "activityLevel": "tres_elevee",
        "lang": "fr",
        "allergies": ["gluten"],
        "createdAt": datetime(2024, 10, 15, 9, 0, 0),
        "updatedAt": datetime(2024, 11, 29, 17, 15, 0)
    },
    {
        "_id": "julie.bertrand@example.com",
        "name": "Julie Bertrand",
        "age": 31,
        "weightKg": 62.0,
        "heightCm": 168,
        "mainGoal": "Flexibilité et bien-être",
        "activityLevel": "moderee",
        "lang": "fr",
        "dietaryPreferences": ["vegetarien"],
        "createdAt": datetime(2024, 11, 1, 11, 0, 0),
        "updatedAt": datetime(2024, 11, 29, 13, 20, 0)
    },
    {
        "_id": "lucas.silva@example.com",
        "name": "Lucas Silva",
        "age": 29,
        "weightKg": 78.0,
        "heightCm": 180,
        "mainGoal": "Développement global",
        "activityLevel": "elevee",
        "lang": "fr",
        "createdAt": datetime(2024, 1, 10, 8, 0, 0),
        "updatedAt": datetime(2024, 11, 28, 10, 0, 0)
    },
]

# Données de recommandations IA historiques (collection 'recommendations')
MONGODB_RECOMMENDATIONS_DATA = [
    {
        "user_id": "marie.dubois@example.com",
        "question": "Profil de l'utilisateur Marie Dubois :\n- Âge : 35 ans\n- Poids : 67.5 kg\n- Taille : 165 cm\n- Objectif principal : Perte de poids\n\nSur ce profil, donne :\n1) un plan d'entraînement simple (3 à 5 séances par semaine max),\n2) quelques conseils d'alimentation et d'hydratation,\n3) un conseil de récupération / sommeil / motivation.",
        "answer": """Bonjour Marie ! Voici votre programme personnalisé :

**Plan d'entraînement (4 séances/semaine):**
- Lundi: Cardio modéré 30 min (marche rapide/vélo)
- Mercredi: Renforcement musculaire 30 min (poids du corps)
- Vendredi: Cardio 40 min (jogging léger)
- Samedi: Yoga/stretching 30 min

**Alimentation:**
- Déficit calorique modéré: ~1400-1500 kcal/jour
- Protéines à chaque repas (œufs, légumineuses, tofu)
- Légumes à volonté, fruits 2-3 portions/jour
- Hydratation: 2L d'eau minimum

**Récupération:**
- Sommeil: 7-9h/nuit (crucial pour perte de poids)
- Repos actif les autres jours (marche légère)
- Gestion du stress: méditation 10 min/jour

Soyez progressive, écoutez votre corps. En cas de douleur, consultez un professionnel.""",
        "createdAt": datetime(2024, 11, 1, 10, 30, 0),
        "age": 35,
        "weightKg": 67.5,
        "heightCm": 165,
        "mainGoal": "Perte de poids",
        "lang": "fr"
    },
    {
        "user_id": "jean.martin@example.com",
        "question": "Profil de l'utilisateur Jean Martin :\n- Âge : 42 ans\n- Poids : 80.5 kg\n- Taille : 178 cm\n- Objectif principal : Gain musculaire\n\nSur ce profil, donne :\n1) un plan d'entraînement simple (3 à 5 séances par semaine max),\n2) quelques conseils d'alimentation et d'hydratation,\n3) un conseil de récupération / sommeil / motivation.",
        "answer": """Bonjour Jean ! Programme pour gain musculaire :

**Plan musculation (4 séances/semaine):**
- Lundi: Pectoraux/Triceps (4 exercices × 3-4 séries × 8-12 reps)
- Mardi: Dos/Biceps (4 exercices × 3-4 séries × 8-12 reps)
- Jeudi: Jambes/Fessiers (5 exercices × 3-4 séries × 8-12 reps)
- Samedi: Épaules/Core (4 exercices × 3-4 séries × 8-12 reps)

**Nutrition prise de masse:**
- Excédent calorique: +300-400 kcal/jour (~2800 kcal)
- Protéines: 1.8-2g/kg soit ~145-160g/jour
- Glucides: post-training prioritaire
- Collations protéinées entre repas

**Récupération:**
- Repos 48h entre mêmes groupes musculaires
- Sommeil: 8-9h (croissance musculaire nocturne)
- Étirements légers post-training

Progression: augmentez charges de 2-5% toutes les 2 semaines. Patience et constance!""",
        "createdAt": datetime(2024, 11, 1, 11, 0, 0),
        "age": 42,
        "weightKg": 80.5,
        "heightCm": 178,
        "mainGoal": "Gain musculaire",
        "lang": "fr"
    },
    {
        "user_id": "pierre.dupont@example.com",
        "question": "Profil de l'utilisateur Pierre Dupont :\n- Âge : 39 ans\n- Poids : 75.8 kg\n- Taille : 175 cm\n- Objectif principal : Endurance\n\nSur ce profil, donne :\n1) un plan d'entraînement simple (3 à 5 séances par semaine max),\n2) quelques conseils d'alimentation et d'hydratation,\n3) un conseil de récupération / sommeil / motivation.",
        "answer": """Bonjour Pierre ! Programme endurance optimisé :

**Plan running (5 séances/semaine):**
- Lundi: Course facile 40 min (zone 2)
- Mardi: Fractionné court (8 × 400m récup 1'30)
- Mercredi: Repos ou cross-training (vélo/natation)
- Jeudi: Course tempo 30 min (zone 3)
- Vendredi: Repos complet
- Samedi: Sortie longue progressive 1h-1h30 (zone 2)
- Dimanche: Récupération active 20 min

**Nutrition runner:**
- Glucides prioritaires: 55-60% apport calorique
- Petit-déj pré-course: toast + banane + café (2h avant)
- Hydratation: 500ml/h d'effort, +électrolytes >1h
- Récup immédiate: glucides + protéines (ratio 3:1)

**Récupération:**
- Sommeil: 8h minimum (adaptations physiologiques)
- Jour de repos complet obligatoire
- Massage/foam roller 2×/semaine

Écoutez vos sensations, la fatigue est un signal. Progressivité = performance durable!""",
        "createdAt": datetime(2024, 11, 15, 7, 30, 0),
        "age": 39,
        "weightKg": 75.8,
        "heightCm": 175,
        "mainGoal": "Endurance",
        "lang": "fr"
    },
]
