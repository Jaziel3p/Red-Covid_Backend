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
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Paciente, Diagnostico, ImagenRad, CustomUser
from .serializers import PacienteSerializer, DiagnosticoSerializer, ImagenRadSerializer, UserSerializer
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from pathlib import Path

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from keras.models import load_model
import keras.models
from PIL import Image





class LimitedGroupGetModelPermissions(DjangoModelPermissions): #Clase personalizada que hereda de DMP para modificar su acceso por default al metodo GET
    def has_permission(self, request, view):                   #para aplicarlo al grupo de usuarios "Trabajador(a)_Social"
        if request.method == 'GET':
            user = request.user
            # Verificar si el usuario tiene permiso
            if user.is_authenticated and user.groups.filter(name__in=['Trabajador(a)_Social']).exists():
                return False
        return super().has_permission(request, view)



class PacienteList(generics.ListCreateAPIView):
    serializer_class = PacienteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        # Filtrar los pacientes por usuario actual
        user = self.request.user.id
        queryset = Paciente.objects.all()
        # if(user == 1):
        #     queryset = Paciente.objects.all()
        # else:
        #     queryset = Paciente.objects.filter(usuario=user)
        
        return queryset
    
class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RangoUsuarioView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        user = request.user
        rango_usuario = user.rango_usuario
        return Response({'rango_usuario': rango_usuario})


from principal.models import Paciente

class DiagnosticoAPIView(APIView):
    def post(self, request):
        probabilidad_covid = request.data.get('probabilidad_covid')
        nota_med = request.data.get('nota')
        id_paciente = request.data.get('id_paciente')
        responsable_diagnostico_id = request.data.get('responsable_diagnostico_id')  # Agregado
        
        resultado_diagnostico = 'P' if probabilidad_covid > 60.0 else 'N'
        
        try:
            ultimo_id_imagen_rad = ImagenRad.objects.latest('id').id
        except ImagenRad.DoesNotExist:
            ultimo_id_imagen_rad = 0
        
        paciente = Paciente.objects.get(id=id_paciente)
        paciente.diagnosticado = True  # Actualizar el campo diagnosticado a True
        paciente.save()
        
        diagnostico = Diagnostico.objects.create(
            resultado_diagnostico=resultado_diagnostico,
            img_rad_id=ultimo_id_imagen_rad,
            nota = nota_med,
            id_paciente=paciente,
            probabilidad_covid=probabilidad_covid,
            responsable_diagnostico_id=responsable_diagnostico_id  # Agregado
        )
        
        return Response({'message': 'Diagnostico creado correctamente'}, status=status.HTTP_201_CREATED)



class PacienteRegistroAPIView(APIView):
    def post(self, request):
        serializer = PacienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePacienteView(APIView):
    def delete(self, request, paciente_id):
        try:
            paciente = Paciente.objects.get(id=paciente_id)
            paciente.delete()
            return Response({"message": "Paciente eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Paciente.DoesNotExist:
            return Response({"message": "El paciente no existe"}, status=status.HTTP_404_NOT_FOUND)

class ImagenRadView(viewsets.ModelViewSet):
    queryset = ImagenRad.objects.all()
    serializer_class = ImagenRadSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    authentication_class = (TokenAuthentication)


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





from .models import Paciente, ImagenRad

class ReportePDF(View):
    def get(self, request, id_paciente, *args, **kwargs):
        try:
            paciente = Paciente.objects.get(id=id_paciente)
            diagnosticos = Diagnostico.objects.filter(id_paciente=id_paciente)
        except Paciente.DoesNotExist:
            return HttpResponse("Paciente no encontrado.")
        except Diagnostico.DoesNotExist:
            return HttpResponse("Diagnóstico no encontrado.")

        for diagnostico in diagnosticos:
            diagnostico.imagen = ImagenRad.objects.get(id=diagnostico.img_rad_id)
            # diagnostico.imagen_url = request.build_absolute_uri(Path(settings.BASE_DIR) /'.'/ diagnostico.imagen.imagen.path)
            imagen_url = Path(settings.BASE_DIR) /'.'/ diagnostico.imagen.imagen.path
            diagnostico.imagen_url = imagen_url.as_uri()
            css_url = './templates/estilos.css'
            LOGOCOVITA = Path(settings.BASE_DIR) /'.'/'templates'/'SVG'/'Mesa de trabajo 1svg.svg'
            LOGOITA = Path(settings.BASE_DIR) /'.'/'templates'/'ITA.png'
        data = {
            'paciente': paciente,
            'diagnosticos': diagnosticos,
            'logo_url':LOGOCOVITA.as_uri(),
            'LogoITA':LOGOITA.as_uri(),
            
        }

        template = get_template("Reporte.html")
        html = template.render(data)

        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(filename=css_url)])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="reporte.pdf"'

        return response

    
#ANALIZAR IMAGEN
class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        paciente_id = request.data.get('id_paciente')
        file_obj = request.FILES['image']

        # Guardar el archivo en el sistema de archivos
        file_path = os.path.join(settings.MEDIA_ROOT, file_obj.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        # Crear una instancia de ImagenRad y guardarla en la base de datos
        imagen_rad = ImagenRad.objects.create(imagen=file_obj, id_paciente_id=paciente_id)

        # Analizar la imagen cargada
        probability = self.analyze_image(file_path)

        # Eliminar el archivo del sistema de archivos
        os.remove(file_path)

        probability = round(probability, 4)  # Redondear a cuatro dígitos después del punto decimal
        return Response({'probability': probability}, status=status.HTTP_200_OK)

    def analyze_image(self, image_path):
        # Cargar el modelo
        model_path = os.path.join(settings.BASE_DIR, 'covid_classifier_model.h5')
        model = load_model(model_path)

        # Preprocesamiento de imagen
        img = image.load_img(image_path, target_size=(200, 200))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalización de píxeles

        # Realizar predicción
        prediction = model.predict(img_array)
        probability = prediction[0][0] * 100

        return probability