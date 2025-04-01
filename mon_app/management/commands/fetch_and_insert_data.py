import requests
import pandas as pd
from sqlalchemy import create_engine
import os
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variables d'environnement pour la configuration
FILE_URL = os.getenv("FILE_URL", "https://www.agence-umoa-titres.com/chemin/vers/fichier.csv")
DB_USER = os.getenv("DB_USER", "utilisateur")
DB_PASSWORD = os.getenv("DB_PASSWORD", "motdepasse")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "umoa_titres")

try:
    # Télécharger le fichier
    logging.info("Téléchargement du fichier CSV...")
    response = requests.get(FILE_URL)
    response.raise_for_status()
    with open("fichier.csv", "wb") as file:
        file.write(response.content)
    logging.info("Fichier téléchargé avec succès.")

    # Lire le fichier CSV
    logging.info("Lecture du fichier CSV...")
    df = pd.read_csv("fichier.csv")

    # Connexion à la base de données MySQL
    logging.info("Connexion à la base de données MySQL...")
    engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

    # Insérer les données dans la table Pays
    logging.info("Insertion des données dans la table Pays...")
    pays_df = df[['pays_code']].drop_duplicates()
    pays_df.to_sql('Pays', con=engine, if_exists='append', index=False)

    # Récupérer les IDs des pays insérés
    with engine.connect() as connection:
        pays_ids = pd.read_sql("SELECT id, nom FROM Pays", connection)
    pays_dict = dict(zip(pays_ids['nom'], pays_ids['id']))

    # Insérer les données dans la table Titre
    logging.info("Insertion des données dans la table Titre...")
    titre_df = df[['isin', 'denomination', 'date_echeance', 'valeur_nominale', 'taux_interet', 'taux_coupon_couru', 'pays_code']]
    titre_df['pays_id'] = titre_df['pays_code'].map(pays_dict)
    titre_df = titre_df.drop(columns=['pays_code'])
    titre_df.to_sql('Titre', con=engine, if_exists='append', index=False)

    # Récupérer les IDs des titres insérés
    with engine.connect() as connection:
        titre_ids = pd.read_sql("SELECT id, isin FROM Titre", connection)
    titre_dict = dict(zip(titre_ids['isin'], titre_ids['id']))

    # Insérer les données dans la table Amortissement
    logging.info("Insertion des données dans la table Amortissement...")
    amortissement_df = df[['isin', 'periode', 'date', 'montant_debut', 'interet', 'amortissement', 'annuite', 'montant_fin']]
    amortissement_df['titre_id'] = amortissement_df['isin'].map(titre_dict)
    amortissement_df = amortissement_df.drop(columns=['isin'])
    amortissement_df.to_sql('Amortissement', con=engine, if_exists='append', index=False)

    logging.info("Données insérées avec succès.")

except requests.RequestException as e:
    logging.error(f"Erreur lors du téléchargement du fichier : {e}")
except pd.errors.EmptyDataError as e:
    logging.error(f"Erreur lors de la lecture du fichier CSV : {e}")
except Exception as e:
    logging.error(f"Erreur inattendue : {e}")

