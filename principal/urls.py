from django.urls import path, include
from .views import PacienteList, DiagnosticoView, ImagenRadView, ReportePDF
from rest_framework import routers
from principal import views

router =  routers.DefaultRouter()
router.register(r'diagnostico', views.DiagnosticoView)
router.register(r'imagen_rad', views.ImagenRadView)

urlpatterns = [
    path('paciente/', PacienteList.as_view(), name='paciente_list'),
    path('reporte/<int:id_paciente>/', ReportePDF.as_view()),
    path('', include(router.urls)),
]