"""
Données mockées pour les journaux alimentaires (Chatbot Service)
"""
from datetime import date, datetime

MEAL_LOGS_DATA = [
    # Journal de Marie (user_id 1) - 3 jours
    {
        "id": 1,
        "user_id": 1,
        "date": date(2024, 11, 25),
        "meal": "breakfast",
        "food": "Porridge avoine (50g) + myrtilles (80g) + amandes effilées (15g)",
        "kcal": 340.0,
        "protein_g": 12.5,
        "carbs_g": 48.0,
        "fat_g": 12.0,
        "notes": "Savoureux et rassasiant",
        "created_at": datetime(2024, 11, 25, 8, 15, 0)
    },
    {
        "id": 2,
        "user_id": 1,
        "date": date(2024, 11, 25),
        "meal": "lunch",
        "food": "Salade quinoa (80g cuit), pois chiches (100g), légumes grillés, vinaigrette olive",
        "kcal": 465.0,
        "protein_g": 18.0,
        "carbs_g": 58.0,
        "fat_g": 16.0,
        "notes": "Très bon, bien rassasiée jusqu'au soir",
        "created_at": datetime(2024, 11, 25, 12, 30, 0)
    },
    {
        "id": 3,
        "user_id": 1,
        "date": date(2024, 11, 25),
        "meal": "dinner",
        "food": "Curry lentilles (150g), riz basmati (60g cru), épinards",
        "kcal": 520.0,
        "protein_g": 22.0,
        "carbs_g": 75.0,
        "fat_g": 12.0,
        "notes": "",
        "created_at": datetime(2024, 11, 25, 19, 0, 0)
    },
    {
        "id": 4,
        "user_id": 1,
        "date": date(2024, 11, 25),
        "meal": "snack",
        "food": "Yaourt grec nature (150g) + pomme",
        "kcal": 145.0,
        "protein_g": 15.0,
        "carbs_g": 18.0,
        "fat_g": 3.0,
        "notes": "Collation post-entraînement",
        "created_at": datetime(2024, 11, 25, 16, 0, 0)
    },
    
    # Journal de Jean (user_id 2) - 2 jours
    {
        "id": 5,
        "user_id": 2,
        "date": date(2024, 11, 26),
        "meal": "breakfast",
        "food": "Omelette 3 œufs + flocons avoine (60g) + banane",
        "kcal": 510.0,
        "protein_g": 32.0,
        "carbs_g": 52.0,
        "fat_g": 18.0,
        "notes": "Boost du matin avant salle",
        "created_at": datetime(2024, 11, 26, 7, 30, 0)
    },
    {
        "id": 6,
        "user_id": 2,
        "date": date(2024, 11, 26),
        "meal": "lunch",
        "food": "Poulet grillé (200g) + riz complet (100g cuit) + brocoli vapeur",
        "kcal": 680.0,
        "protein_g": 58.0,
        "carbs_g": 65.0,
        "fat_g": 15.0,
        "notes": "Repas post-training parfait",
        "created_at": datetime(2024, 11, 26, 13, 0, 0)
    },
    {
        "id": 7,
        "user_id": 2,
        "date": date(2024, 11, 26),
        "meal": "snack",
        "food": "Shake protéiné whey (30g) + lait amande + fraises",
        "kcal": 245.0,
        "protein_g": 28.0,
        "carbs_g": 18.0,
        "fat_g": 6.0,
        "notes": "Immédiatement après musculation",
        "created_at": datetime(2024, 11, 26, 11, 15, 0)
    },
    
    # Journal de Sophie (user_id 3) - 2 jours
    {
        "id": 8,
        "user_id": 3,
        "date": date(2024, 11, 27),
        "meal": "breakfast",
        "food": "Smoothie bowl açai + granola maison (40g) + fruits frais",
        "kcal": 395.0,
        "protein_g": 9.0,
        "carbs_g": 62.0,
        "fat_g": 14.0,
        "notes": "Délicieux et coloré!",
        "created_at": datetime(2024, 11, 27, 8, 45, 0)
    },
    {
        "id": 9,
        "user_id": 3,
        "date": date(2024, 11, 27),
        "meal": "lunch",
        "food": "Burger végétal maison (haricots noirs) + frites patate douce",
        "kcal": 540.0,
        "protein_g": 18.0,
        "carbs_g": 72.0,
        "fat_g": 20.0,
        "notes": "Repas réconfort vegan",
        "created_at": datetime(2024, 11, 27, 12, 20, 0)
    },
    {
        "id": 10,
        "user_id": 3,
        "date": date(2024, 11, 27),
        "meal": "dinner",
        "food": "Chili sin carne (lentilles, haricots rouges) + riz complet",
        "kcal": 515.0,
        "protein_g": 22.0,
        "carbs_g": 78.0,
        "fat_g": 12.0,
        "notes": "",
        "created_at": datetime(2024, 11, 27, 19, 30, 0)
    },
    
    # Journal de Pierre (user_id 4) - running day
    {
        "id": 11,
        "user_id": 4,
        "date": date(2024, 11, 28),
        "meal": "breakfast",
        "food": "Toast pain complet + beurre cacahuète (20g) + banane + café",
        "kcal": 385.0,
        "protein_g": 12.0,
        "carbs_g": 58.0,
        "fat_g": 14.0,
        "notes": "Petit-déj pré-course 10km",
        "created_at": datetime(2024, 11, 28, 6, 30, 0)
    },
    {
        "id": 12,
        "user_id": 4,
        "date": date(2024, 11, 28),
        "meal": "lunch",
        "food": "Pâtes complètes (100g sec) + sauce tomate + thon (120g) + parmesan",
        "kcal": 625.0,
        "protein_g": 42.0,
        "carbs_g": 85.0,
        "fat_g": 14.0,
        "notes": "Recharge glucides après course",
        "created_at": datetime(2024, 11, 28, 13, 15, 0)
    },
    {
        "id": 13,
        "user_id": 4,
        "date": date(2024, 11, 28),
        "meal": "snack",
        "food": "Barre énergétique maison (dattes + noix)",
        "kcal": 180.0,
        "protein_g": 5.0,
        "carbs_g": 28.0,
        "fat_g": 7.0,
        "notes": "Snack pré-course",
        "created_at": datetime(2024, 11, 28, 9, 0, 0)
    },
]
