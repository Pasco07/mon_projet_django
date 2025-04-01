from django.core.management.base import BaseCommand
from mon_app.utils.umoa_titres import scrape_umoa_titres

class Command(BaseCommand):
    help = "Scrape les données des titres depuis le site de l'Agence UMOA-Titres"

    def handle(self, *args, **kwargs):
        scrape_umoa_titres()
        self.stdout.write(self.style.SUCCESS('Données scrapées avec succès !'))