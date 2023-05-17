from django.contrib import admin
from .models import Diagnostico, ImagenRad, Paciente
#from .serializers import UserSerializer

admin.site.register(Diagnostico)
admin.site.register(ImagenRad)
admin.site.register(Paciente)
#admin.site.register(UserSerializer)
