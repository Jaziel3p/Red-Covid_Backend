from rest_framework import serializers
from .models import CustomUser
from .models import Paciente, Diagnostico, ImagenRad

class UserSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    cedula = serializers.CharField()
    nombres = serializers.CharField()
    apellido_p = serializers.CharField()
    apellido_m = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    rango_usuario = serializers.CharField()

    def create(self, validated_data):
        instance = CustomUser() 
        instance.cedula = validated_data.get('cedula')
        instance.nombres = validated_data.get('nombres')
        instance.apellido_p = validated_data.get('apellido_p')
        instance.apellido_m = validated_data.get('apellido_m')
        instance.username = validated_data.get('username')
        instance.email = validated_data.get('email')
        instance.set_password(validated_data.get('password'))
        instance.rango_usuario = validated_data.get('rango_usuario')
        instance.save()
        return instance
    
    def validated_username(self, data):
        users = CustomUser.objects.filter(username = data)
        if len(users) != 0:
            raise serializers.ValidationError("Nombre de Usuario ya existente")
        else:
            return data
        

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__' #invoca todos los campos


class ImagenRadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenRad
        fields = '__all__'


class DiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnostico
        fields = '__all__'