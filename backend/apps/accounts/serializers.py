from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario
from .validators import ValidacaoCompleta

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
    """Serializer para edição de usuários com validações de segurança"""
    password = serializers.CharField(write_only=True, required=False)
    password_atual = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'telefone', 'is_active', 'groups', 'date_joined',
            'last_login', 'password', 'password_atual'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def validate(self, attrs):
        """Aplicar todas as validações de segurança"""
        request = self.context.get('request')
        usuario_atual = request.user if request else None
        usuario_target = self.instance
        
        if not usuario_atual:
            raise serializers.ValidationError("Usuário não autenticado")
        
        # ✅ APLICAR TODAS AS VALIDAÇÕES CRÍTICAS
        ValidacaoCompleta.validar_edicao_usuario(usuario_atual, usuario_target, attrs)
        
        # Validação específica de senha
        if 'password' in attrs:
            if not attrs.get('password_atual'):
                # Se não é o próprio usuário, admin pode alterar sem senha atual
                if usuario_atual.id == usuario_target.id:
                    raise serializers.ValidationError({
                        'password_atual': 'Senha atual é obrigatória para alteração.'
                    })
            else:
                # Verificar senha atual
                if not check_password(attrs['password_atual'], usuario_target.password):
                    raise serializers.ValidationError({
                        'password_atual': 'Senha atual incorreta.'
                    })
        
        # Remover password_atual dos dados (não salvar no banco)
        attrs.pop('password_atual', None)
        
        return attrs
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Atualizar campos normais
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Atualizar senha se fornecida
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer customizado para login com email"""
    username_field = 'email'
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Marcar usuário como online
        if hasattr(self.user, 'set_online'):
            self.user.set_online()
        else:
            self.user.is_online = True
            self.user.save()
        
        # ADICIONAR dados do usuário na resposta
        from .serializers import UsuarioBasicoSerializer
        data['user'] = UsuarioBasicoSerializer(self.user).data
        
        return data