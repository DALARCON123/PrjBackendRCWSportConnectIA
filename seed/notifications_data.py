"""
Données mockées pour les notifications (Auth Service)
"""
from datetime import datetime

NOTIFICATIONS_DATA = [
    {
        "id": 1,
        "user_id": 2,
        "title": "Bienvenue sur SportConnectIA",
        "message": "Nous sommes ravis de vous accueillir ! N'hésitez pas à explorer nos services.",
        "is_read": True,
        "created_at": datetime(2024, 2, 20, 14, 50, 0)
    },
    {
        "id": 2,
        "user_id": 2,
        "title": "Nouvelle fonctionnalité disponible",
        "message": "Le coach IA nutritionnel est maintenant disponible. Essayez-le !",
        "is_read": False,
        "created_at": datetime(2024, 11, 20, 10, 15, 0)
    },
    {
        "id": 3,
        "user_id": 3,
        "title": "Rappel d'entraînement",
        "message": "N'oubliez pas votre séance de fitness aujourd'hui !",
        "is_read": True,
        "created_at": datetime(2024, 11, 15, 8, 0, 0)
    },
    {
        "id": 4,
        "user_id": 3,
        "title": "Félicitations !",
        "message": "Vous avez atteint votre objectif hebdomadaire de 5 séances !",
        "is_read": False,
        "created_at": datetime(2024, 11, 25, 18, 30, 0)
    },
    {
        "id": 5,
        "user_id": 4,
        "title": "Conseil du jour",
        "message": "Pensez à bien vous hydrater avant et après votre course !",
        "is_read": True,
        "created_at": datetime(2024, 11, 10, 7, 0, 0)
    },
    {
        "id": 6,
        "user_id": 5,
        "title": "Nouveau programme de yoga",
        "message": "Un nouveau programme de yoga pour débutants est disponible.",
        "is_read": False,
        "created_at": datetime(2024, 11, 28, 9, 30, 0)
    },
    {
        "id": 7,
        "user_id": 8,
        "title": "Maintenance programmée",
        "message": "Le service sera en maintenance le 5 décembre de 2h à 4h du matin.",
        "is_read": False,
        "created_at": datetime(2024, 11, 29, 16, 0, 0)
    },
]
