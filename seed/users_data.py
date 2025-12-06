"""
Données mockées pour les utilisateurs (Auth Service)
"""
from datetime import datetime

# -------------------------------------------------------
# Mots de passe hashés avec bcrypt
# Format: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
# -------------------------------------------------------

USERS_DATA = [
    {
        "id": 1,
        "name": "Marie Dubois",
        "email": "marie.dubois@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/9eFVO",  # Mot de passe: password123
        "is_active": True,
        "is_admin": True,
        "created_at": datetime(2024, 1, 15, 10, 30, 0)
    },
    {
        "id": 2,
        "name": "Jean Martin",
        "email": "jean.martin@example.com",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: sport2024
        "is_active": True,
        "is_admin": False,
        "created_at": datetime(2024, 2, 20, 14, 45, 0)
    },
    {
        "id": 3,
        "name": "Sophie Laurent",
        "email": "sophie.laurent@example.com",
        "password_hash": "$2b$12$KIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: fitness123
        "is_active": True,
        "is_admin": False,
        "created_at": datetime(2024, 3, 10, 9, 15, 0)
    },
    {
        "id": 4,
        "name": "Pierre Dupont",
        "email": "pierre.dupont@example.com",
        "password_hash": "$2b$12$MIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: running2024
        "is_active": True,
        "is_admin": False,
        "created_at": datetime(2024, 4, 5, 16, 20, 0)
    },
    {
        "id": 5,
        "name": "Julie Bertrand",
        "email": "julie.bertrand@example.com",
        "password_hash": "$2b$12$NIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: yoga2024
        "is_active": True,
        "is_admin": False,
        "created_at": datetime(2024, 5, 12, 11, 0, 0)
    },
    {
        "id": 6,
        "name": "Lucas Silva",
        "email": "lucas.silva@example.com",
        "password_hash": "$2b$12$OIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: admin123
        "is_active": True,
        "is_admin": True,
        "created_at": datetime(2024, 1, 10, 8, 0, 0)
    },
    {
        "id": 7,
        "name": "Emma Wilson",
        "email": "emma.wilson@example.com",
        "password_hash": "$2b$12$PIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: wellness123
        "is_active": False,
        "is_admin": False,
        "created_at": datetime(2024, 6, 18, 13, 30, 0)
    },
    {
        "id": 8,
        "name": "Thomas Bernard",
        "email": "thomas.bernard@example.com",
        "password_hash": "$2b$12$QIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mot de passe: strength123
        "is_active": True,
        "is_admin": False,
        "created_at": datetime(2024, 7, 25, 15, 45, 0)
    },
    {
        "id": 9,
        "name": "Diana Alarcon",
        "email": "dianaalarcon@teccart.com",
        "password_hash": "$2b$12$0PKgWJRyYelUqoINDJdQB.x9/zFc6Ae.XTS7BPW1GinSEQC4C1eEy",  # Mot de passe: Admin123!
        "is_active": True,
        "is_admin": True,
        "created_at": datetime(2024, 8, 1, 9, 0, 0)
    },
]
