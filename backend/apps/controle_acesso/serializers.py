from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import GrupoCustomizado, PermissaoCustomizada
from accounts.models import Usuario

class PermissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class PermissaoCustomizadaSerializer(serializers.ModelSerializer):
    modulo_display = serializers.SerializerMethodField()
    acao_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissaoCustomizada
        fields = [
            'id', 'modulo', 'modulo_display', 'acao', 'acao_display',
            'nome', 'descricao', 'auto_descoberta', 'ativo', 'created_at'
        ]
    
    def get_modulo_display(self, obj):
        return obj.modulo.replace('_', ' ').title()
    
    def get_acao_display(self, obj):
        return obj.acao.title()

class GrupoCustomizadoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='group.name')
    total_usuarios = serializers.ReadOnlyField()
    total_permissoes = serializers.ReadOnlyField()
    usuarios = serializers.SerializerMethodField()
    permissoes = serializers.SerializerMethodField()
    
    class Meta:
        model = GrupoCustomizado
        fields = [
            'id', 'nome', 'descricao', 'ativo', 
            'total_usuarios', 'total_permissoes',
            'usuarios', 'permissoes',
            'created_at', 'updated_at'
        ]
    
    def get_usuarios(self, obj):
        usuarios = obj.group.user_set.all()
        return [{'id': u.id, 'username': u.username, 'email': u.email} for u in usuarios]
    
    def get_permissoes(self, obj):
        permissoes = obj.group.permissions.all()
        return [{'id': p.id, 'name': p.name, 'codename': p.codename} for p in permissoes]
    
    def create(self, validated_data):
        group_data = validated_data.pop('group')
        nome = group_data['name']
        
        # Criar o Group do Django
        group = Group.objects.create(name=nome)
        
        # Criar o GrupoCustomizado
        grupo_customizado = GrupoCustomizado.objects.create(
            group=group,
            **validated_data
        )
        
        return grupo_customizado
    
    def update(self, instance, validated_data):
        group_data = validated_data.pop('group', None)
        
        if group_data:
            instance.group.name = group_data.get('name', instance.group.name)
            instance.group.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UsuarioComGruposSerializer(serializers.ModelSerializer):
    """Serializer para usuários com informações de grupos"""
    grupos = serializers.SerializerMethodField()
    total_grupos = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'is_active', 'is_online', 'grupos', 'total_grupos'
        ]
    
    def get_grupos(self, obj):
        grupos = obj.groups.all()
        return [{'id': g.id, 'name': g.name} for g in grupos]
    
    def get_total_grupos(self, obj):
        return obj.groups.count()

class AdicionarUsuariosGrupoSerializer(serializers.Serializer):
    """Serializer para adicionar usuários a um grupo"""
    usuarios_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs dos usuários"
    )

class AdicionarPermissoesGrupoSerializer(serializers.Serializer):
    """Serializer para adicionar permissões a um grupo"""
    permissoes_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs das permissões"
    )

class UsuarioSimplificadoSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem em grupos"""
    class Meta:
        model = Usuario
        fields = ['id', 'username']
    
    def to_representation(self, instance):
        # Só incluir usuários ativos
        if not instance.is_active:
            return None
        return super().to_representation(instance)

class GrupoSimplificadoSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de grupos do usuário"""
    id = serializers.IntegerField(source='group.id')
    nome = serializers.CharField(source='group.name')
    
    class Meta:
        model = GrupoCustomizado
        fields = ['id', 'nome']
    
    def to_representation(self, instance):
        # Só incluir grupos ativos
        if not instance.ativo:
            return None
        return super().to_representation(instance)