# umoa_titres/urls.py
from django.conf import settings
from django.conf.urls.static  import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mon_app.urls')),  # Point d'entrée principal
]