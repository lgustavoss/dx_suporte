from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from apps.controle_acesso.models import GrupoCustomizado, PermissaoCustomizada
from apps.accounts.models import Usuario

class PermissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class PermissaoCustomizadaSerializer(serializers.ModelSerializer):
    modulo_display = serializers.SerializerMethodField()
    acao_display = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissaoCustomizada
        fields = [
            'id', 'modulo', 'modulo_display', 'acao', 'acao_display',
            'nome', 'descricao', 'auto_descoberta', 'ativo', 
            'created_at', 'updated_at', 'label'
        ]
    
    def get_modulo_display(self, obj):
        return obj.modulo.replace('_', ' ').title()

    def get_acao_display(self, obj):
        return obj.acao.title()

    def get_label(self, obj):
        # Mapeamento por modulo/acao para nomes amigáveis
        map = {
            ('accounts', 'criar'): 'Criar usuário',
            ('accounts', 'excluir'): 'Excluir usuário',
            ('accounts', 'editar'): 'Editar usuário',
            ('accounts', 'visualizar'): 'Visualizar usuário',
            ('accounts', 'gerenciar'): 'Gerenciar usuários',
            ('controle_acesso', 'criar'): 'Criar grupo',
            ('controle_acesso', 'excluir'): 'Excluir grupo',
            ('controle_acesso', 'editar'): 'Editar grupo',
            ('controle_acesso', 'visualizar'): 'Visualizar grupo',
            ('controle_acesso', 'gerenciar'): 'Gerenciar grupos',
        }
        key = (obj.modulo, obj.acao)
        if key in map:
            return map[key]
        # Se houver descrição, retorna
        if obj.descricao:
            return obj.descricao
        # Gera label genérica
        acao_map = {
            'criar': 'Criar',
            'excluir': 'Excluir',
            'editar': 'Editar',
            'visualizar': 'Visualizar',
            'gerenciar': 'Gerenciar',
        }
        modulo_map = {
            'accounts': 'usuário',
            'controle_acesso': 'grupo',
        }
        return f"{acao_map.get(obj.acao, obj.acao.title())} {modulo_map.get(obj.modulo, obj.modulo.replace('_', ' '))}"  

class GroupSerializer(serializers.ModelSerializer):
    """Serializer para Django Group"""
    class Meta:
        model = Group
        fields = ['id', 'name']

class GrupoCustomizadoSerializer(serializers.ModelSerializer):
    """Serializer para grupos customizados"""
    
    # ✅ USAR DOIS CAMPOS DIFERENTES: um para leitura, outro para escrita
    group = GroupSerializer(read_only=True)
    nome = serializers.CharField(source='group.name', read_only=True)
    total_usuarios = serializers.IntegerField(read_only=True)
    total_permissoes = serializers.IntegerField(read_only=True)
    group_data = GroupSerializer(write_only=True, required=False)

    class Meta:
        model = GrupoCustomizado
        fields = [
            'id', 'nome', 'group', 'group_data', 'descricao', 'ativo',
            'total_usuarios', 'total_permissoes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'nome', 'total_usuarios', 'total_permissoes']
    
    def create(self, validated_data):
        """Criar grupo customizado com grupo Django aninhado"""
        # ✅ EXTRAIR dados do grupo aninhado
        group_data = validated_data.pop('group_data', None)
        
        if not group_data:
            raise serializers.ValidationError({
                'group_data': 'Este campo é obrigatório para criação.'
            })
        
        group_name = group_data['name']
        
        # ✅ VERIFICAR se nome já existe
        if Group.objects.filter(name=group_name).exists():
            existing_group = Group.objects.get(name=group_name)
            # Verificar se já tem GrupoCustomizado
            if hasattr(existing_group, 'custom_group'):
                raise serializers.ValidationError({
                    'group_data': {'name': ['Já existe um grupo customizado para este nome.']}
                })
            # Se não tem, usar o grupo existente
            group_django = existing_group
        else:
            # Criar novo grupo
            group_django = Group.objects.create(name=group_name)
        
        # ✅ CRIAR grupo customizado
        grupo_custom = GrupoCustomizado.objects.create(
            group=group_django,
            **validated_data
        )
        
        return grupo_custom
    
    def update(self, instance, validated_data):
        """Atualizar grupo customizado"""
        # ✅ TRATAR atualização do grupo aninhado
        group_data = validated_data.pop('group_data', None)
        
        if group_data:
            group_name = group_data.get('name')
            if group_name and group_name != instance.group.name:
                # Verificar se novo nome já existe
                if Group.objects.filter(name=group_name).exclude(id=instance.group.id).exists():
                    raise serializers.ValidationError({
                        'group_data': {'name': ['Já existe um grupo com este nome.']}
                    })
                
                instance.group.name = group_name
                instance.group.save()
        
        # ✅ ATUALIZAR outros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Customizar representação de saída"""
        data = super().to_representation(instance)
        # ✅ COMPATIBILIDADE: Também incluir group.id para testes antigos
        if 'group' in data and isinstance(data['group'], dict):
            data['group_id'] = data['group']['id']
        
        # Remover group_data da saída (só é usado na entrada)
        data.pop('group_data', None)
        return data

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