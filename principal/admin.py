from django.contrib import admin
# from .models import Diagnostico, ImagenRad, Paciente
from .models import Paciente
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

# admin.site.register(Diagnostico)
# admin.site.register(ImagenRad)
admin.site.register(Paciente)
#admin.site.register(UserSerializer)
