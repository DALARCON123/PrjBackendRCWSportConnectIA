"""
Script principal de seeding pour la base de données SportConnectIA
Popule toutes les tables des différents services avec des données mockées

Usage:
    python seed/seeder.py --all                    # Popule toutes les tables
    python seed/seeder.py --auth                   # Popule uniquement Auth Service
    python seed/seeder.py --chatbot                # Popule uniquement Chatbot Service
    python seed/seeder.py --tracking               # Popule uniquement Tracking/Metrics (MongoDB)
    python seed/seeder.py --mongodb                # Popule uniquement MongoDB (users et recommandations)
    python seed/seeder.py --clear                  # Supprime toutes les données avant seeding
"""

import sys
import os
from pathlib import Path

# -------------------------------------------------------
# Ajouter le répertoire racine au PYTHONPATH
# -------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import argparse

# -------------------------------------------------------
# Charger les variables d'environnement
# -------------------------------------------------------
load_dotenv(ROOT_DIR / ".env")

# -------------------------------------------------------
# Configuration de la base de données PostgreSQL
# -------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/sportconnect")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------
# Configuration MongoDB
# -------------------------------------------------------
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGODB_DB_NAME", "RCW")


def seed_auth_service(clear_first: bool = False):
    """
    Popule les tables du Auth Service (PostgreSQL):
    - users
    - notifications
    """
    print("\n" + "=" * 60)
    print("SEEDING AUTH SERVICE (PostgreSQL)")
    print("=" * 60)
    
    from services.auth_service_fastapi.app.models import User, Notification
    from services.auth_service_fastapi.app.db import Base
    from seed.users_data import USERS_DATA
    from seed.notifications_data import NOTIFICATIONS_DATA
    
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        if clear_first:
            print("🗑️  Suppression des données existantes...")
            session.query(Notification).delete()
            session.query(User).delete()
            session.commit()
            print("✅ Données supprimées")
        
        # Insérer les utilisateurs
        print(f"\n📥 Insertion de {len(USERS_DATA)} utilisateurs...")
        for user_data in USERS_DATA:
            # Vérifier si l'utilisateur existe déjà
            existing = session.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"⚠️  Utilisateur {user_data['email']} existe déjà, ignoré")
                continue
            
            user = User(**user_data)
            session.add(user)
            print(f"   ✓ {user_data['name']} ({user_data['email']})")
        
        session.commit()
        print(f"✅ {len(USERS_DATA)} utilisateurs insérés")
        
        # Insérer les notifications
        print(f"\n📥 Insertion de {len(NOTIFICATIONS_DATA)} notifications...")
        inserted_count = 0
        for notif_data in NOTIFICATIONS_DATA:
            # Vérifier si la notification existe déjà
            existing = session.query(Notification).filter(Notification.id == notif_data["id"]).first()
            if existing:
                print(f"⚠️  Notification id={notif_data['id']} existe déjà, ignorée")
                continue
            
            notification = Notification(**notif_data)
            session.add(notification)
            print(f"   ✓ Notification pour user_id={notif_data['user_id']}: {notif_data['title']}")
            inserted_count += 1
        
        session.commit()
        print(f"✅ {inserted_count} notifications insérées")
        
    except Exception as e:
        print(f"❌ Erreur lors du seeding Auth Service: {e}")
        session.rollback()
        raise
    finally:
        session.close()
    
    print("\n✅ AUTH SERVICE SEEDING TERMINÉ")


def seed_chatbot_service(clear_first: bool = False):
    """
    Popule les tables du Chatbot Service (PostgreSQL):
    - coach_users
    - coach_interactions
    - coach_meal_plans
    - coach_meal_logs
    """
    print("\n" + "=" * 60)
    print("SEEDING CHATBOT SERVICE (PostgreSQL)")
    print("=" * 60)
    
    from services.chatbot_service_fastapi.app.models import User, Interaction, MealPlan, MealLog, Base
    from seed.coach_users_data import COACH_USERS_DATA
    from seed.interactions_data import INTERACTIONS_DATA
    from seed.meal_plans_data import MEAL_PLANS_DATA
    from seed.meal_logs_data import MEAL_LOGS_DATA
    
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        if clear_first:
            print("🗑️  Suppression des données existantes...")
            session.query(MealLog).delete()
            session.query(MealPlan).delete()
            session.query(Interaction).delete()
            session.query(User).delete()
            session.commit()
            print("✅ Données supprimées")
        
        # Insérer les utilisateurs du coach
        print(f"\n📥 Insertion de {len(COACH_USERS_DATA)} utilisateurs coach...")
        for user_data in COACH_USERS_DATA:
            existing = session.query(User).filter(User.external_id == user_data["external_id"]).first()
            if existing:
                print(f"⚠️  Coach user {user_data['external_id']} existe déjà, ignoré")
                continue
            
            user = User(**user_data)
            session.add(user)
            print(f"   ✓ Coach user: {user_data['external_id']}")
        
        session.commit()
        print(f"✅ {len(COACH_USERS_DATA)} utilisateurs coach insérés")
        
        # Insérer les interactions
        print(f"\n📥 Insertion de {len(INTERACTIONS_DATA)} interactions...")
        inserted_count = 0
        for interaction_data in INTERACTIONS_DATA:
            # Vérifier si l'interaction existe déjà
            existing = session.query(Interaction).filter(Interaction.id == interaction_data["id"]).first()
            if existing:
                print(f"⚠️  Interaction id={interaction_data['id']} existe déjà, ignorée")
                continue
            
            interaction = Interaction(**interaction_data)
            session.add(interaction)
            print(f"   ✓ Interaction {interaction_data['kind']} pour user_id={interaction_data['user_id']}")
            inserted_count += 1
        
        session.commit()
        print(f"✅ {inserted_count} interactions insérées")
        
        # Insérer les plans alimentaires
        print(f"\n📥 Insertion de {len(MEAL_PLANS_DATA)} plans alimentaires...")
        inserted_count = 0
        for plan_data in MEAL_PLANS_DATA:
            # Vérifier si le plan existe déjà
            existing = session.query(MealPlan).filter(MealPlan.id == plan_data["id"]).first()
            if existing:
                print(f"⚠️  Plan alimentaire id={plan_data['id']} existe déjà, ignoré")
                continue
            
            meal_plan = MealPlan(**plan_data)
            session.add(meal_plan)
            print(f"   ✓ Plan alimentaire {plan_data['week']} pour user_id={plan_data['user_id']}")
            inserted_count += 1
        
        session.commit()
        print(f"✅ {inserted_count} plans alimentaires insérés")
        
        # Insérer les logs alimentaires
        print(f"\n📥 Insertion de {len(MEAL_LOGS_DATA)} logs alimentaires...")
        inserted_count = 0
        for log_data in MEAL_LOGS_DATA:
            # Vérifier si le log existe déjà
            existing = session.query(MealLog).filter(MealLog.id == log_data["id"]).first()
            if existing:
                print(f"⚠️  Log alimentaire id={log_data['id']} existe déjà, ignoré")
                continue
            
            meal_log = MealLog(**log_data)
            session.add(meal_log)
            print(f"   ✓ Log {log_data['meal']} le {log_data['date']} pour user_id={log_data['user_id']}")
            inserted_count += 1
        
        session.commit()
        print(f"✅ {inserted_count} logs alimentaires insérés")
        
    except Exception as e:
        print(f"❌ Erreur lors du seeding Chatbot Service: {e}")
        session.rollback()
        raise
    finally:
        session.close()
    
    print("\n✅ CHATBOT SERVICE SEEDING TERMINÉ")


def seed_tracking_mongodb(clear_first: bool = False):
    """
    Popule MongoDB avec les mesures corporelles (données des capteurs et métriques de santé)
    """
    print("\n" + "=" * 60)
    print("SEEDING TRACKING/METRICS SERVICE (MongoDB)")
    print("=" * 60)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
        from seed.tracking_data import MEASUREMENTS_DATA
        
        # Tenter de se connecter avec un timeout court
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Tester la connexion
        try:
            client.server_info()
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print("⚠️  MongoDB n'est pas accessible. Service sera ignoré.")
            print(f"    Détail: {type(e).__name__}")
            print("    💡 Conseil: Démarrez MongoDB ou utilisez --auth --chatbot")
            return
        
        db = client[MONGO_DB]
        measurements_collection = db["health_metrics"]
        
        if clear_first:
            print("🗑️  Suppression des données existantes...")
            measurements_collection.delete_many({})
            print("✅ Données supprimées")
        
        # Insérer les mesures corporelles
        print(f"\n📥 Insertion de {len(MEASUREMENTS_DATA)} mesures corporelles...")
        for measurement in MEASUREMENTS_DATA:
            measurements_collection.insert_one(measurement)
            print(f"   ✓ Mesure du {measurement['date']} pour {measurement['email']}")
        
        print(f"✅ {len(MEASUREMENTS_DATA)} mesures insérées")
        
    except ImportError:
        print("⚠️  pymongo n'est pas installé. Installez-le avec: pip install pymongo")
        print("    Service MongoDB sera ignoré.")
        return
    except Exception as e:
        print(f"⚠️  Erreur lors du seeding MongoDB tracking: {e}")
        print("    Service sera ignoré.")
        return
    
    print("\n✅ TRACKING MONGODB SEEDING TERMINÉ")


def seed_mongodb(clear_first: bool = False):
    """
    Popule MongoDB avec les profils utilisateurs et recommandations
    """
    print("\n" + "=" * 60)
    print("SEEDING MONGODB")
    print("=" * 60)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
        from seed.mongodb_data import MONGODB_USERS_DATA, MONGODB_RECOMMENDATIONS_DATA
        
        # Tenter de se connecter avec un timeout court
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Tester la connexion
        try:
            client.server_info()
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print("⚠️  MongoDB n'est pas accessible. Service sera ignoré.")
            print(f"    Détail: {type(e).__name__}")
            print("    💡 Conseil: Démarrez MongoDB ou utilisez --auth --chatbot --tracking")
            return
        
        db = client[MONGO_DB]
        
        users_collection = db["users"]
        recommendations_collection = db["recommendations"]
        
        if clear_first:
            print("🗑️  Suppression des données existantes...")
            users_collection.delete_many({})
            recommendations_collection.delete_many({})
            print("✅ Données supprimées")
        
        # Insérer les profils utilisateurs
        print(f"\n📥 Insertion de {len(MONGODB_USERS_DATA)} profils utilisateurs...")
        for user_data in MONGODB_USERS_DATA:
            # Vérifier si l'utilisateur existe déjà
            existing = users_collection.find_one({"_id": user_data["_id"]})
            if existing:
                print(f"⚠️  Utilisateur {user_data['_id']} existe déjà, mise à jour...")
                users_collection.replace_one({"_id": user_data["_id"]}, user_data)
            else:
                users_collection.insert_one(user_data)
                print(f"   ✓ {user_data['name']} ({user_data['_id']})")
        
        print(f"✅ {len(MONGODB_USERS_DATA)} profils utilisateurs insérés")
        
        # Insérer les recommandations
        print(f"\n📥 Insertion de {len(MONGODB_RECOMMENDATIONS_DATA)} recommandations...")
        for reco_data in MONGODB_RECOMMENDATIONS_DATA:
            recommendations_collection.insert_one(reco_data)
            print(f"   ✓ Recommandation pour {reco_data['user_id']}")
        
        print(f"✅ {len(MONGODB_RECOMMENDATIONS_DATA)} recommandations insérées")
        
    except ImportError:
        print("⚠️  pymongo n'est pas installé. Installez-le avec: pip install pymongo")
        print("    Service MongoDB sera ignoré.")
        return
    except Exception as e:
        print(f"⚠️  Erreur lors du seeding MongoDB: {e}")
        print("    Service MongoDB sera ignoré. Les autres services continuent.")
        return
    
    print("\n✅ MONGODB SEEDING TERMINÉ")


def main():
    """
    Point d'entrée principal du script
    """
    parser = argparse.ArgumentParser(description="Script de seeding pour SportConnectIA")
    parser.add_argument("--all", action="store_true", help="Popule toutes les bases de données")
    parser.add_argument("--auth", action="store_true", help="Popule Auth Service uniquement")
    parser.add_argument("--chatbot", action="store_true", help="Popule Chatbot Service uniquement")
    parser.add_argument("--tracking", action="store_true", help="Popule MongoDB tracking/metrics uniquement")
    parser.add_argument("--mongodb", action="store_true", help="Popule MongoDB uniquement")
    parser.add_argument("--clear", action="store_true", help="Supprime les données avant seeding")
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher l'aide
    if not any([args.all, args.auth, args.chatbot, args.tracking, args.mongodb]):
        parser.print_help()
        return
    
    print("\n" + "🌱" * 30)
    print("  SPORTCONNECTIA - DATABASE SEEDING")
    print("🌱" * 30)
    
    success_count = 0
    error_count = 0
    
    try:
        if args.all or args.auth:
            try:
                seed_auth_service(clear_first=args.clear)
                success_count += 1
            except Exception as e:
                print(f"\n❌ ERREUR Auth Service: {e}")
                error_count += 1
        
        if args.all or args.chatbot:
            try:
                seed_chatbot_service(clear_first=args.clear)
                success_count += 1
            except Exception as e:
                print(f"\n❌ ERREUR Chatbot Service: {e}")
                error_count += 1
        
        if args.all or args.tracking:
            try:
                seed_tracking_mongodb(clear_first=args.clear)
                success_count += 1
            except Exception as e:
                print(f"\n❌ ERREUR Tracking MongoDB: {e}")
                error_count += 1
        
        if args.all or args.mongodb:
            try:
                seed_mongodb(clear_first=args.clear)
                success_count += 1
            except Exception as e:
                print(f"\n❌ ERREUR MongoDB: {e}")
                error_count += 1
        
        print("\n" + "🎉" * 30)
        if error_count == 0:
            print("  SEEDING TERMINÉ AVEC SUCCÈS!")
        else:
            print(f"  SEEDING TERMINÉ: {success_count} succès, {error_count} erreur(s)")
        print("🎉" * 30)
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
