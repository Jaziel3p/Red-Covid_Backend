from django.urls import path, include
from .views import PacienteList, DiagnosticoView, ImagenRadView
from rest_framework import routers
from principal import views

router =  routers.DefaultRouter()
router.register(r'diagnostico', views.DiagnosticoView)
router.register(r'imagen_rad', views.ImagenRadView)

urlpatterns = [
    path('paciente/', PacienteList.as_view(), name='paciente_list'),
    path('', include(router.urls)),
]