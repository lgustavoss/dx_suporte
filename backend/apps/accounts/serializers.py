from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario
from django.contrib.auth.hashers import check_password

class UsuarioBasicoSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de usuários"""
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'is_active', 
            'is_online'
        ]

class UsuarioDetalhadoSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do usuário"""
    total_grupos = serializers.SerializerMethodField()
    grupos_nomes = serializers.SerializerMethodField()
    tempo_offline_formatado = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'full_name',
            'telefone',
            'is_active', 
            'is_online',
            'date_joined',
            'last_login',
            'last_activity',
            'logout_time',
            'tempo_offline_formatado',
            'total_grupos',
            'grupos_nomes'
        ]
    
    def get_total_grupos(self, obj):
        return obj.groups.count()
    
    def get_grupos_nomes(self, obj):
        return [grupo.name for grupo in obj.groups.all()]
    
    def get_full_name(self, obj):
        """Retorna nome completo do usuário"""
        return obj.get_full_name() or obj.username
    
    def get_tempo_offline_formatado(self, obj):
        """Retorna tempo offline formatado"""
        tempo = obj.tempo_offline()
        if tempo:
            total_seconds = int(tempo.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return None

class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuários"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'telefone'
        ]
    
    def validate(self, data):
        """Validar senhas"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        return data
    
    def create(self, validated_data):
        """Criar usuário com senha criptografada"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        
        return usuario

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer ÚNICO para edição de usuários"""
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    tempo_offline_formatado = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'telefone', 'is_online', 'last_activity',
            'logout_time', 'tempo_offline_formatado', 'is_active',
            'date_joined', 'created_at', 'updated_at',
            'password', 'password_confirm', 'current_password'
        ]
        read_only_fields = [
            'id', 'is_online', 'last_activity', 'logout_time',
            'date_joined', 'created_at', 'updated_at'
        ]
    
    def validate(self, attrs):
        """Validações customizadas - APENAS quando alterando senha"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        current_password = attrs.get('current_password')
        
        # APENAS se está tentando alterar senha
        if password or password_confirm:
            if not current_password:
                raise serializers.ValidationError({
                    'current_password': 'Senha atual é obrigatória para alterar a senha.'
                })
            
            user = self.instance
            if user and not check_password(current_password, user.password):
                raise serializers.ValidationError({
                    'current_password': 'Senha atual incorreta.'
                })
            
            if password != password_confirm:
                raise serializers.ValidationError({
                    'password_confirm': 'As senhas não coincidem.'
                })
                
            if user and check_password(password, user.password):
                raise serializers.ValidationError({
                    'password': 'A nova senha deve ser diferente da atual.'
                })
        
        # Limpar campos auxiliares
        attrs.pop('password_confirm', None)
        attrs.pop('current_password', None)
        return attrs
    
    def update(self, instance, validated_data):
        """Update customizado para handle da senha"""
        password = validated_data.pop('password', None)
        
        # Atualizar campos normais
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Atualizar senha se fornecida
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
    
    def get_full_name(self, obj):
        """Retorna nome completo do usuário"""
        return obj.get_full_name() or obj.username
    
    def get_tempo_offline_formatado(self, obj):
        """Retorna tempo offline formatado"""
        tempo = obj.tempo_offline()
        if tempo:
            total_seconds = int(tempo.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return None

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer customizado para login com email"""
    username_field = 'email'