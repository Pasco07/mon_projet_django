import psycopg2

try:
    conn = psycopg2.connect(
        host="dpg-cvlt3n6mcj7s73e9muug-a.oregon-postgres.render.com",
        dbname="mtp",
        user="root",
        password="",
        sslmode="require"
    )
    print("Connexion réussie !")
    conn.close()
except Exception as e:
    print(f"Échec de connexion : {e}")