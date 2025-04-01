
from django.urls import path
from . import views

urlpatterns = [
    path('', views.select_pays, name='select_pays'),
    path('get-titres-data/', views.get_titres_data, name='get_titres_data'),
    path('titre/<str:isin>/', views.titre_detail, name='titre_detail'),
]

