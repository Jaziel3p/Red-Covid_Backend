from django.contrib import admin
from django.urls import path, include
from principal.api import UserAPI
from principal.views import Login, Logout, Username, ImageUploadView, PacienteRegistroAPIView, DiagnosticoAPIView, DeletePacienteView, ReportePDF, UserRegistrationAPIView, RangoUsuarioView
from rest_framework.authtoken import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/create_user/', UserAPI.as_view(), name='create_user'),
    path('principal/', include(('principal.urls', 'principal_urls'))),
    path('api_generate_token/', views.obtain_auth_token),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('api/get_username/', Username.as_view(), name='get_username'),
    path('api/upload_image/', ImageUploadView.as_view(), name='upload_image'),
    path('api/registro/', PacienteRegistroAPIView.as_view(), name='PacienteRegistroAPIView'),
    path('api/diagnostico/', DiagnosticoAPIView.as_view(), name='DiagnosticoAPIView'),
    path('api/delete/<paciente_id>/', DeletePacienteView.as_view(), name='DeletePaciente'),
     path('reporte/<int:id_paciente>/', ReportePDF.as_view(), name='reporte_pdf'),
     path('resgistrarUsuario/', UserRegistrationAPIView.as_view(), name='UserRegistrationAPIView'),
     path('rango-usuario/', RangoUsuarioView.as_view(), name='rango-usuario'),
]  


