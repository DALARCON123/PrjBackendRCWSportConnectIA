"""
Données mockées pour les utilisateurs du coach IA (Chatbot Service)
"""
import json

COACH_USERS_DATA = [
    {
        "id": 1,
        "external_id": "marie.dubois@example.com",
        "profile": json.dumps({
            "age": 35,
            "weight_kg": 65,
            "height_cm": 165,
            "goal": "Perte de poids",
            "activity_level": "moderee",
            "dietary_preferences": ["vegetarien"],
            "allergies": []
        })
    },
    {
        "id": 2,
        "external_id": "jean.martin@example.com",
        "profile": json.dumps({
            "age": 42,
            "weight_kg": 82,
            "height_cm": 178,
            "goal": "Gain musculaire",
            "activity_level": "elevee",
            "dietary_preferences": [],
            "allergies": ["lactose"]
        })
    },
    {
        "id": 3,
        "external_id": "sophie.laurent@example.com",
        "profile": json.dumps({
            "age": 28,
            "weight_kg": 58,
            "height_cm": 160,
            "goal": "Maintien forme",
            "activity_level": "moderee",
            "dietary_preferences": ["vegan"],
            "allergies": []
        })
    },
    {
        "id": 4,
        "external_id": "pierre.dupont@example.com",
        "profile": json.dumps({
            "age": 39,
            "weight_kg": 75,
            "height_cm": 175,
            "goal": "Endurance",
            "activity_level": "tres_elevee",
            "dietary_preferences": [],
            "allergies": ["gluten"]
        })
    },
    {
        "id": 5,
        "external_id": "julie.bertrand@example.com",
        "profile": json.dumps({
            "age": 31,
            "weight_kg": 62,
            "height_cm": 168,
            "goal": "Flexibilité et bien-être",
            "activity_level": "moderee",
            "dietary_preferences": ["vegetarien"],
            "allergies": []
        })
    },
]
