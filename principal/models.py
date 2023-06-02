from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, User



class CustomUser(AbstractUser): #Agregando campos al modelo usuario que usa por defecto Django 
    cedula = models.CharField(max_length=12)
    nombres = models.CharField(max_length=50)
    apellido_p = models.CharField(max_length=50)
    apellido_m = models.CharField(max_length=50)
    email = models.EmailField()
    rango_usuario = models.CharField(max_length=50)
    
    def __str__(self):
        return f'Usuario {self.id}: {self.username}'


class Paciente(models.Model):
    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pacientes',
        null=True,  # Permitir valores nulos
        blank=True,  # Permitir campos en blanco
    )
    NSS = models.CharField(max_length=11)
    nombres = models.CharField(max_length=50)
    apellido_p = models.CharField(max_length=50)
    apellido_m = models.CharField(max_length=50)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    altura = models.DecimalField(max_digits=3, decimal_places=2)
    peso = models.DecimalField(max_digits=4, decimal_places=1)
    enfermedades = models.CharField(max_length=300, blank=True)
    tipo_sangre = models.CharField(max_length=3)
    fecha_nacimiento = models.DateField()
    telefono = models.IntegerField()
    correo_e = models.EmailField()
    diagnosticado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return f'Paciente {self.id}: {self.NSS} {self.apellido_p} {self.apellido_m} {self.nombres}'




class ImagenRad(models.Model):
    fecha_captura = models.DateField(auto_now_add=True)
    imagen = models.ImageField(upload_to='imagenesRadPacientes')
    id_paciente  = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'imagen'
        verbose_name_plural = 'imagenes'

    def __str__(self):
        return f'Imagen de: {self.id_paciente.NSS} {self.id_paciente.apellido_p} {self.id_paciente.apellido_m} {self.id_paciente.nombres}'




class Diagnostico(models.Model):
    DIAGNOSTICO_CHOICES = [('P', 'Positivo'), ('N', 'Negativo')]
    
    fecha_diagnostico = models.DateField(auto_now_add=True)
    resultado_diagnostico = models.CharField(max_length=1, choices=DIAGNOSTICO_CHOICES)
    probabilidad_covid = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    img_rad = models.ForeignKey(ImagenRad, on_delete=models.CASCADE)
    nota = models.CharField(max_length=500, default="No hay nota medica")
    responsable_diagnostico = models.ForeignKey(CustomUser, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'diagnóstico'
        verbose_name_plural = 'diagnósticos'

    def __str__(self):
        return f'Diagnóstico {self.id}: {self.fecha_diagnostico} {self.id_paciente}'

