import requests
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal
import logging
from django.core.exceptions import ValidationError
from mon_app.models import Pays, Titre

logger = logging.getLogger(__name__)

def fetch_umoa_titres():
    url = "https://www.umoatitres.org/fr/agence-umoa-titres-agence-regionale-dappui-a-lemission-a-gestion-titres-publics-lumoa/emissions-professionnels-3/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception si la requête échoue
    except requests.RequestException as e:
        logger.error(f"Erreur lors de la récupération des données : {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        logger.warning("Aucun tableau trouvé sur la page.")
        return []

    rows = table.find_all('tr')
    data = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 7:  # Assurez-vous que la ligne contient suffisamment de colonnes
            try:
                cleaned_row = {
                    'pays_code': cells[0].text.strip(),
                    'type_titre': cells[1].text.strip(),
                    'isin': cells[2].text.strip(),
                    'denomination': cells[3].text.strip(),
                    'date_echeance': datetime.strptime(cells[4].text.strip(), '%d/%m/%Y').date(),
                    'valeur_nominale': Decimal(cells[5].text.strip().replace(',', '')),
                    'taux_interet': Decimal(cells[6].text.strip().replace('%', ''))
                }
                data.append(cleaned_row)
            except (ValueError, IndexError) as e:
                logger.error(f"Erreur lors du nettoyage des données : {e}")
    return data

def save_to_database(data):
    for item in data:
        try:
            pays, created = Pays.objects.get_or_create(nom=item['pays_code'])
            titre, created = Titre.objects.get_or_create(
                isin=item['isin'],
                defaults={
                    'pays': pays,
                    'type_titre': item['type_titre'],
                    'denomination': item['denomination'],
                    'date_echeance': item['date_echeance'],
                    'valeur_nominale': item['valeur_nominale'],
                    'taux_interet': item['taux_interet']
                }
            )
            if not created:
                logger.info(f"Le titre avec l'ISIN {item['isin']} existe déjà.")
        except ValidationError as e:
            logger.error(f"Erreur de validation pour l'ISIN {item['isin']} : {e}")

def fetch_and_save_umoa_titres():
    data = fetch_umoa_titres()
    save_to_database(data)
    logger.info("Données enregistrées avec succès.")