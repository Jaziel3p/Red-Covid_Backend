from django.urls import path
from .views import PacienteList

urlpatterns = [
    path('paciente/', PacienteList.as_view(), name='paciente_list'),
]