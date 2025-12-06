"""
Données mockées pour les plans alimentaires (Chatbot Service)
"""
from datetime import datetime

MEAL_PLANS_DATA = [
    {
        "id": 1,
        "user_id": 1,
        "week": "2024-W45",
        "summary": "Plan alimentaire végétarien pour perte de poids progressive (déficit 400 kcal/jour)",
        "details": """Lundi:
- Petit-déj: Porridge avoine + fruits rouges + amandes (350 kcal)
- Déjeuner: Salade complète quinoa, pois chiches, légumes grillés (450 kcal)
- Dîner: Curry de lentilles, riz basmati, légumes (500 kcal)
- Collation: Yaourt grec + pomme (150 kcal)

Mardi:
- Petit-déj: Toast complet, avocat, œuf poché (380 kcal)
- Déjeuner: Bowl Buddha tofu, patate douce, brocoli (480 kcal)
- Dîner: Soupe minestrone + pain complet (420 kcal)
- Collation: Fruits secs mélangés 30g (140 kcal)

[... reste de la semaine similaire]""",
        "kcal_target": 1450,
        "protein_g": 80,
        "carbs_g": 180,
        "fat_g": 45,
        "created_at": datetime(2024, 11, 4, 10, 0, 0)
    },
    {
        "id": 2,
        "user_id": 2,
        "week": "2024-W46",
        "summary": "Plan hyperprotéiné pour gain musculaire (excédent 300 kcal/jour)",
        "details": """Lundi:
- Petit-déj: Omelette 3 œufs, flocons d'avoine, banane (520 kcal)
- Déjeuner: Poulet grillé 200g, riz complet, brocoli (680 kcal)
- Dîner: Saumon 150g, quinoa, asperges (620 kcal)
- Collations: Shake protéiné + fruits (250 kcal x2)

Mardi:
- Petit-déj: Pancakes protéinés, beurre d'amande (480 kcal)
- Déjeuner: Bœuf maigre 180g, patate douce, salade (700 kcal)
- Dîner: Thon, pâtes complètes, légumes (650 kcal)
- Collations: Cottage cheese + noix (220 kcal x2)

[... reste de la semaine similaire]""",
        "kcal_target": 2800,
        "protein_g": 200,
        "carbs_g": 320,
        "fat_g": 80,
        "created_at": datetime(2024, 11, 11, 9, 30, 0)
    },
    {
        "id": 3,
        "user_id": 3,
        "week": "2024-W47",
        "summary": "Plan vegan équilibré pour maintien (2000 kcal/jour)",
        "details": """Lundi:
- Petit-déj: Smoothie bowl açai, granola, fruits (400 kcal)
- Déjeuner: Burger végétal maison, frites patate douce (550 kcal)
- Dîner: Chili sin carne, riz complet (520 kcal)
- Collations: Houmous + crudités (180 kcal), Energy balls (150 kcal)

Mardi:
- Petit-déj: Toast avocat, tofu brouillé, jus d'orange (420 kcal)
- Déjeuner: Pad thaï tofu, légumes (580 kcal)
- Dîner: Curry pois chiches, naan maison (540 kcal)
- Collations: Lait doré curcuma (120 kcal), Fruits frais (140 kcal)

[... reste de la semaine similaire]""",
        "kcal_target": 2000,
        "protein_g": 90,
        "carbs_g": 260,
        "fat_g": 65,
        "created_at": datetime(2024, 11, 18, 11, 15, 0)
    },
]
