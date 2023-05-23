from rest_framework import generics
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.template.loader import get_template
from weasyprint import CSS, HTML

from .models import Paciente, Diagnostico, ImagenRad
from .models import Paciente
from .serializers import PacienteSerializer, DiagnosticoSerializer, ImagenRadSerializer
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes



class LimitedGroupGetModelPermissions(DjangoModelPermissions): #Clase personalizada que hereda de DMP para modificar su acceso por default al metodo GET
    def has_permission(self, request, view):                   #para aplicarlo al grupo de usuarios "Trabajador(a)_Social"
        if request.method == 'GET':
            user = request.user
            # Verificar si el usuario tiene permiso
            if user.is_authenticated and user.groups.filter(name__in=['Trabajador(a)_Social']).exists():
                return False
        return super().has_permission(request, view)



class PacienteList(generics.ListCreateAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    authentication_class = (TokenAuthentication,)


class DiagnosticoView(viewsets.ModelViewSet):
    queryset = Diagnostico.objects.all()
    serializer_class = DiagnosticoSerializer
    permission_classes = (IsAuthenticated, LimitedGroupGetModelPermissions)
    authentication_class = (TokenAuthentication,)


class ImagenRadView(viewsets.ModelViewSet):
    queryset = ImagenRad.objects.all()
    serializer_class = ImagenRadSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    authentication_class = (TokenAuthentication,)


class Login(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('principal_urls:paciente_list') # django_api.urls.py  ubicacion | name

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(Login, self).dispatch(request, *args, *kwargs)
        
    def form_valid(self, form):
        user = authenticate(username = form.cleaned_data['username'], password = form.cleaned_data['password'])
        token,_ = Token.objects.get_or_create(user = user)
        if token:
            login(self.request, form.get_user())
            return super(Login, self).form_valid(form)

class Username(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        username = request.user.username
        # Realiza alguna acción con el nombre de usuario
        return Response({'username': username})   
        

class Logout(APIView):
    
    def get(self, request, format=None):
        if request.user.is_authenticated:
            # Verificar si el usuario tiene un token de autenticación
            if hasattr(request.user, 'auth_token'):
                # Eliminar el token de autenticación
                Token.objects.filter(user=request.user).delete()
        
        # Cerrar la sesión del usuario
        logout(request)
        
        return Response(status=status.HTTP_200_OK)
    

class ReportePDF(View):
    def get(self, request, id_paciente, *args, **kwargs):
        paciente = Paciente.objects.get(id=id_paciente)
        diagnostico = Diagnostico.objects.get(id=id_paciente)

        data = {
            'paciente': paciente,
            'diagnostico': diagnostico,
        }

        template = get_template("ReportePDF.html")
        html = template.render(data)
        #css_url
        pdf = HTML(string=html).write_pdf()

        return HttpResponse(pdf, content_type='application/pdf')
