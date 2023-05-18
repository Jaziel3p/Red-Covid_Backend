from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Paciente, Diagnostico, ImagenRad

class UserSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    cedula = serializers.CharField()
    nombres = serializers.CharField()
    apellidos = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    tipo_usuario = serializers.CharField()

    def create(self, validated_data):
        instance = User()
        instance.cedula = validated_data.get('cedula')
        instance.nombres = validated_data.get('nombres')
        instance.apellidos = validated_data.get('apellidos')
        instance.username = validated_data.get('username')
        instance.email = validated_data.get('email')
        instance.set_password(validated_data.get('password'))
        instance.tipo_usuario = validated_data.get('tipo_usuario')
        instance.save()
        return instance
    
    def validated_username(self, data):
        users = User.objects.filter(username = data)
        if len(users) != 0:
            raise serializers.ValidationError("Nombre de Usuario ya existente")
        else:
            return data
        

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__' #invoca todos los campos