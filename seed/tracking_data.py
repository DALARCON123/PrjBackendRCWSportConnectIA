"""
Données mockées pour les mesures corporelles (Reco Service - MongoDB)
Utilise MongoDB pour stocker les données des capteurs et métriques de santé
"""

MEASUREMENTS_DATA = [
    # Mesures de Marie (marie.dubois@example.com)
    {
        "id": 1,
        "email": "marie.dubois@example.com",
        "date": "2024-11-01",
        "weight_kg": 67.5,
        "waist_cm": 78.0,
        "hips_cm": 98.0,
        "chest_cm": 92.0,
        "notes": "Début du programme perte de poids"
    },
    {
        "id": 2,
        "email": "marie.dubois@example.com",
        "date": "2024-11-08",
        "weight_kg": 66.8,
        "waist_cm": 77.0,
        "hips_cm": 97.5,
        "chest_cm": 91.5,
        "notes": "Première semaine - bonne progression"
    },
    {
        "id": 3,
        "email": "marie.dubois@example.com",
        "date": "2024-11-15",
        "weight_kg": 66.2,
        "waist_cm": 76.5,
        "hips_cm": 97.0,
        "chest_cm": 91.0,
        "notes": "Continue sur la bonne voie"
    },
    {
        "id": 4,
        "email": "marie.dubois@example.com",
        "date": "2024-11-22",
        "weight_kg": 65.6,
        "waist_cm": 76.0,
        "hips_cm": 96.5,
        "chest_cm": 90.5,
        "notes": "Objectif: atteindre 64kg"
    },
    {
        "id": 5,
        "email": "marie.dubois@example.com",
        "date": "2024-11-29",
        "weight_kg": 65.0,
        "waist_cm": 75.5,
        "hips_cm": 96.0,
        "chest_cm": 90.0,
        "notes": "Excellent progrès ce mois!"
    },
    
    # Mesures de Jean (jean.martin@example.com) - gain musculaire
    {
        "id": 6,
        "email": "jean.martin@example.com",
        "date": "2024-11-01",
        "weight_kg": 80.5,
        "waist_cm": 85.0,
        "hips_cm": 98.0,
        "chest_cm": 102.0,
        "notes": "Début programme prise de masse"
    },
    {
        "id": 7,
        "email": "jean.martin@example.com",
        "date": "2024-11-15",
        "weight_kg": 81.8,
        "waist_cm": 85.5,
        "hips_cm": 98.5,
        "chest_cm": 103.5,
        "notes": "Bonne prise de masse propre"
    },
    {
        "id": 8,
        "email": "jean.martin@example.com",
        "date": "2024-11-29",
        "weight_kg": 82.5,
        "waist_cm": 86.0,
        "hips_cm": 99.0,
        "chest_cm": 104.5,
        "notes": "Pectoraux en progression visible"
    },
    
    # Mesures de Sophie (sophie.laurent@example.com) - maintien
    {
        "id": 9,
        "email": "sophie.laurent@example.com",
        "date": "2024-11-01",
        "weight_kg": 58.2,
        "waist_cm": 68.0,
        "hips_cm": 92.0,
        "chest_cm": 86.0,
        "notes": "Poids stable, objectif maintien"
    },
    {
        "id": 10,
        "email": "sophie.laurent@example.com",
        "date": "2024-11-15",
        "weight_kg": 58.0,
        "waist_cm": 67.5,
        "hips_cm": 92.0,
        "chest_cm": 86.0,
        "notes": "Parfait équilibre"
    },
    {
        "id": 11,
        "email": "sophie.laurent@example.com",
        "date": "2024-11-29",
        "weight_kg": 58.3,
        "waist_cm": 68.0,
        "hips_cm": 92.5,
        "chest_cm": 86.5,
        "notes": "Légère fluctuation normale"
    },
    
    # Mesures de Pierre (pierre.dupont@example.com) - runner
    {
        "id": 12,
        "email": "pierre.dupont@example.com",
        "date": "2024-10-15",
        "weight_kg": 76.5,
        "waist_cm": 82.0,
        "hips_cm": 96.0,
        "chest_cm": 98.0,
        "notes": "Début entraînement marathon"
    },
    {
        "id": 13,
        "email": "pierre.dupont@example.com",
        "date": "2024-11-01",
        "weight_kg": 75.8,
        "waist_cm": 81.0,
        "hips_cm": 95.5,
        "chest_cm": 97.5,
        "notes": "Volume d'entraînement élevé"
    },
    {
        "id": 14,
        "email": "pierre.dupont@example.com",
        "date": "2024-11-15",
        "weight_kg": 75.2,
        "waist_cm": 80.5,
        "hips_cm": 95.0,
        "chest_cm": 97.0,
        "notes": "Affûtage en cours"
    },
    {
        "id": 15,
        "email": "pierre.dupont@example.com",
        "date": "2024-11-29",
        "weight_kg": 75.0,
        "waist_cm": 80.0,
        "hips_cm": 95.0,
        "chest_cm": 97.0,
        "notes": "Forme olympique pour le marathon!"
    },
    
    # Mesures de Julie (julie.bertrand@example.com) - yoga
    {
        "id": 16,
        "email": "julie.bertrand@example.com",
        "date": "2024-11-01",
        "weight_kg": 62.0,
        "waist_cm": 70.0,
        "hips_cm": 94.0,
        "chest_cm": 88.0,
        "notes": "Pratique yoga régulière"
    },
    {
        "id": 17,
        "email": "julie.bertrand@example.com",
        "date": "2024-11-15",
        "weight_kg": 62.2,
        "waist_cm": 70.0,
        "hips_cm": 94.0,
        "chest_cm": 88.0,
        "notes": "Souplesse et tonicité améliorées"
    },
    {
        "id": 18,
        "email": "julie.bertrand@example.com",
        "date": "2024-11-29",
        "weight_kg": 62.0,
        "waist_cm": 69.5,
        "hips_cm": 94.0,
        "chest_cm": 88.0,
        "notes": "Posture excellente, corps tonifié"
    },
]
