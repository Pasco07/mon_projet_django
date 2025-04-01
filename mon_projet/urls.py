# umoa_titres/urls.py
from django.conf import settings
from django.conf.urls.static  import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mon_app.urls')),  # Point d'entrée principal
]

urlpatterns += staticfiles_urlpatterns()