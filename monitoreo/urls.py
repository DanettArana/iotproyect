from django.urls import path
from . import views

urlpatterns = [
    path("data/", views.api_data),  # Endpoint legacy para compatibilidad
    path("recibir/", views.recibir_dato),
    path("api/latest/", views.api_latest, name="api_latest"),
    path("api/history/", views.api_history, name="api_history"),
]
