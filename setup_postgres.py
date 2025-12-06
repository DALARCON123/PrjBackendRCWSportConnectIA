"""
Script pour configurer PostgreSQL avec l'utilisateur et la base de données corrects
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Essayer différentes combinaisons utilisateur/mot de passe communes
CREDENTIALS = [
    ('postgres', ''),
    ('postgres', 'postgres'),
    ('postgres', '1234'),
    ('postgres', 'admin'),
    ('postgres', 'admin123'),
    ('admin', 'admin123'),
]

TARGET_USER = 'admin'
TARGET_PASSWORD = 'admin123'
TARGET_DB = 'sportconnect'

def find_working_credentials():
    """Essaie de trouver des identifiants qui fonctionnent"""
    for user, password in CREDENTIALS:
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user=user,
                password=password,
                database='postgres'
            )
            print(f"✓ Connecté avec succès en utilisant : user={user}")
            return conn, user, password
        except psycopg2.OperationalError as e:
            continue
    return None, None, None

def setup_database():
    """Configure l'utilisateur et la base de données"""
    conn, working_user, working_password = find_working_credentials()
    
    if not conn:
        print("\n❌ Impossible de se connecter à PostgreSQL avec les identifiants connus.")
        print("\nVeuillez exécuter manuellement dans PostgreSQL :")
        print(f"  CREATE USER {TARGET_USER} WITH PASSWORD '{TARGET_PASSWORD}';")
        print(f"  CREATE DATABASE {TARGET_DB} OWNER {TARGET_USER};")
        print(f"  GRANT ALL PRIVILEGES ON DATABASE {TARGET_DB} TO {TARGET_USER};")
        sys.exit(1)
    
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (TARGET_USER,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            print(f"\n📝 Création de l'utilisateur '{TARGET_USER}'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(TARGET_USER)),
                (TARGET_PASSWORD,)
            )
            print(f"✓ Utilisateur '{TARGET_USER}' créé avec succès")
        else:
            print(f"\n✓ L'utilisateur '{TARGET_USER}' existe déjà. Mise à jour du mot de passe...")
            cursor.execute(
                sql.SQL("ALTER USER {} WITH PASSWORD %s").format(sql.Identifier(TARGET_USER)),
                (TARGET_PASSWORD,)
            )
            print(f"✓ Mot de passe de l'utilisateur '{TARGET_USER}' mis à jour")
        
        # Vérifier si la base de données existe déjà
        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (TARGET_DB,))
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"\n📝 Création de la base de données '{TARGET_DB}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(TARGET_DB),
                    sql.Identifier(TARGET_USER)
                )
            )
            print(f"✓ Base de données '{TARGET_DB}' créée avec succès")
        else:
            print(f"\n✓ La base de données '{TARGET_DB}' existe déjà")
        
        # Accorder les privilèges
        print(f"\n📝 Attribution des privilèges...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(TARGET_DB),
                sql.Identifier(TARGET_USER)
            )
        )
        print(f"✓ Privilèges accordés à l'utilisateur '{TARGET_USER}'")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ Configuration de PostgreSQL terminée avec succès !")
        print("="*60)
        print(f"\nIdentifiants configurés :")
        print(f"  Host: localhost")
        print(f"  Port: 5432")
        print(f"  User: {TARGET_USER}")
        print(f"  Password: {TARGET_PASSWORD}")
        print(f"  Database: {TARGET_DB}")
        print(f"\nURL de connexion :")
        print(f"  postgresql://{TARGET_USER}:{TARGET_PASSWORD}@localhost:5432/{TARGET_DB}")
        
        # Tester la connexion avec les nouveaux identifiants
        print(f"\n🧪 Test de connexion avec les nouveaux identifiants...")
        test_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user=TARGET_USER,
            password=TARGET_PASSWORD,
            database=TARGET_DB
        )
        print("✅ Test de connexion réussi !")
        test_conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur pendant la configuration : {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
