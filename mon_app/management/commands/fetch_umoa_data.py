from django.core.management.base import BaseCommand
from mon_app.utils.umoa_titres import fetch_and_save_umoa_titres

class Command(BaseCommand):
    help = "Récupère les données des titres UMOA et les enregistre dans la base de données."

    def handle(self, *args, **kwargs):
        fetch_and_save_umoa_titres()
        self.stdout.write(self.style.SUCCESS('Données enregistrées avec succès.'))