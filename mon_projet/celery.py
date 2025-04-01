import os
from celery import Celery

# Définir le module Django par défaut pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mon_projet.settings')

# Créer une instance de Celery
app = Celery('mon_projet')

# Charger la configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les applications Django
app.autodiscover_tasks()