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
            print(f"✓ Conectado com sucesso usando: user={user}")
            return conn, user, password
        except psycopg2.OperationalError as e:
            continue
    return None, None, None

def setup_database():
    """Configure l'utilisateur et la base de données"""
    conn, working_user, working_password = find_working_credentials()
    
    if not conn:
        print("\n❌ Não foi possível conectar ao PostgreSQL com nenhuma credencial conhecida.")
        print("\nPor favor, execute manualmente no PostgreSQL:")
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
            print(f"\n📝 Criando usuário '{TARGET_USER}'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(TARGET_USER)),
                (TARGET_PASSWORD,)
            )
            print(f"✓ Usuário '{TARGET_USER}' criado com sucesso")
        else:
            print(f"\n✓ Usuário '{TARGET_USER}' já existe. Atualizando senha...")
            cursor.execute(
                sql.SQL("ALTER USER {} WITH PASSWORD %s").format(sql.Identifier(TARGET_USER)),
                (TARGET_PASSWORD,)
            )
            print(f"✓ Senha do usuário '{TARGET_USER}' atualizada")
        
        # Vérifier si la base de données existe déjà
        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (TARGET_DB,))
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"\n📝 Criando banco de dados '{TARGET_DB}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(TARGET_DB),
                    sql.Identifier(TARGET_USER)
                )
            )
            print(f"✓ Banco de dados '{TARGET_DB}' criado com sucesso")
        else:
            print(f"\n✓ Banco de dados '{TARGET_DB}' já existe")
        
        # Accorder les privilèges
        print(f"\n📝 Concedendo privilégios...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(TARGET_DB),
                sql.Identifier(TARGET_USER)
            )
        )
        print(f"✓ Privilégios concedidos ao usuário '{TARGET_USER}'")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ Configuração do PostgreSQL concluída com sucesso!")
        print("="*60)
        print(f"\nCredenciais configuradas:")
        print(f"  Host: localhost")
        print(f"  Port: 5432")
        print(f"  User: {TARGET_USER}")
        print(f"  Password: {TARGET_PASSWORD}")
        print(f"  Database: {TARGET_DB}")
        print(f"\nURL de conexão:")
        print(f"  postgresql://{TARGET_USER}:{TARGET_PASSWORD}@localhost:5432/{TARGET_DB}")
        
        # Tester la connexion avec les nouveaux identifiants
        print(f"\n🧪 Testando conexão com as novas credenciais...")
        test_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user=TARGET_USER,
            password=TARGET_PASSWORD,
            database=TARGET_DB
        )
        print("✅ Teste de conexão bem-sucedido!")
        test_conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro durante a configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
