# umoa_titres/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mon_app.urls')),  # Point d'entrée principal
]