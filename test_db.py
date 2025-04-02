# test_db.py
import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement

def test_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'dpg-cvlt3n6mcj7s73e9muug-a.oregon-postgres.render.com'),
            dbname=os.getenv('DB_NAME', 'mtp'),
            user=os.getenv('DB_USER', 'mtp_user'),
            password=os.getenv('DB_PASSWORD', ''),
            sslmode="require",
            connect_timeout=10
        )
        print("✅ Connexion réussie à PostgreSQL!")
        
        # Vérification des tables existantes
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📋 Tables existantes: {tables}")
        
        # Vérification spécifique de la table mon_app_pays
        if 'mon_app_pays' in tables:
            print("✅ Table mon_app_pays existe")
        else:
            print("❌ Table mon_app_pays manquante - Les migrations doivent être appliquées")
        
        conn.close()
        return True
        
    except OperationalError as e:
        print(f"❌ Échec de connexion: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    test_connection()