from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import Usuario

class ValidacaoSeguranca:
    """Validações críticas de segurança do sistema"""
    
    @staticmethod
    def validar_nao_autoexclusao(usuario_atual, usuario_target):
        """1. Não permitir que usuário se exclua"""
        if usuario_atual.id == usuario_target.id:
            raise serializers.ValidationError({
                "detail": "❌ Você não pode excluir sua própria conta."
            })
    
    @staticmethod
    def validar_nao_autodesativacao(usuario_atual, usuario_target, dados):
        """3. Não permitir que usuário desative própria conta"""
        if usuario_atual.id == usuario_target.id:
            if 'is_active' in dados and not dados['is_active']:
                raise serializers.ValidationError({
                    "is_active": "❌ Você não pode desativar sua própria conta."
                })
    
    @staticmethod
    def validar_ultimo_administrador(usuario_target, dados=None):
        """1. Não permitir remover/desativar último administrador"""
        # Se está sendo desativado via dados
        desativando = dados and 'is_active' in dados and not dados['is_active']
        
        # Se já está inativo e não está sendo alterado, não precisa validar
        if not usuario_target.is_active and not desativando:
            return
            
        # Verificar se é administrador
        admin_groups = Group.objects.filter(
            name__icontains='admin'
        )
        
        if not usuario_target.groups.filter(id__in=admin_groups).exists():
            return  # Não é admin, pode desativar
        
        # Contar administradores ativos (excluindo o atual se está sendo desativado/excluído)
        admins_ativos = Usuario.objects.filter(
            is_active=True,
            groups__in=admin_groups
        ).distinct()
        
        # Se está sendo desativado ou "excluído", excluir da contagem
        if desativando or dados is None:  # dados=None indica exclusão
            admins_ativos = admins_ativos.exclude(id=usuario_target.id)
        
        if admins_ativos.count() == 0:
            raise serializers.ValidationError({
                "detail": "❌ Não é possível desativar o último administrador do sistema."
            })
    
    @staticmethod
    def validar_hierarquia_edicao(usuario_atual, usuario_target):
        """4. Apenas admins podem editar outros admins"""
        # Se é o próprio usuário, pode editar (dados básicos)
        if usuario_atual.id == usuario_target.id:
            return
            
        # Se é superuser, pode editar qualquer um
        if usuario_atual.is_superuser:
            return
            
        # Verificar se target é admin
        admin_groups = Group.objects.filter(
            name__icontains='admin'
        )
        
        target_is_admin = usuario_target.groups.filter(id__in=admin_groups).exists()
        current_is_admin = usuario_atual.groups.filter(id__in=admin_groups).exists()
        
        if target_is_admin and not current_is_admin:
            raise serializers.ValidationError({
                "detail": "❌ Apenas administradores podem editar outros administradores."
            })
    
    @staticmethod
    def validar_edicao_propria_conta(usuario_atual, usuario_target, dados):
        """5. Usuários só podem editar dados próprios (limitados)"""
        if usuario_atual.id != usuario_target.id:
            # Se não é o próprio usuário, verificar se pode editar outros
            ValidacaoSeguranca.validar_hierarquia_edicao(usuario_atual, usuario_target)
        else:
            # Se é o próprio usuário, limitar campos que pode editar
            campos_proprios_permitidos = [
                'first_name', 'last_name', 'email', 'telefone', 
                'password', 'password_atual'
            ]
            
            campos_proibidos = []
            for campo in dados.keys():
                if campo not in campos_proprios_permitidos:
                    campos_proibidos.append(campo)
            
            if campos_proibidos:
                raise serializers.ValidationError({
                    "detail": f"❌ Você não pode alterar os campos: {', '.join(campos_proibidos)}"
                })
    
    @staticmethod
    def validar_grupos_sensiveis(usuario_atual, usuario_target, dados):
        """6. Validar alteração de grupos sensíveis"""
        if 'groups' not in dados:
            return
            
        # Se não é admin nem superuser, não pode alterar grupos
        if not usuario_atual.is_superuser:
            admin_groups = Group.objects.filter(name__icontains='admin')
            if not usuario_atual.groups.filter(id__in=admin_groups).exists():
                raise serializers.ValidationError({
                    "groups": "❌ Apenas administradores podem alterar grupos de usuários."
                })
        
        # Verificar se está tentando adicionar/remover grupos de admin
        novos_grupos = dados.get('groups', [])
        grupos_atuais = list(usuario_target.groups.values_list('id', flat=True))
        
        admin_groups_ids = list(Group.objects.filter(
            name__icontains='admin'
        ).values_list('id', flat=True))
        
        # Se está removendo grupos de admin, validar último admin
        removendo_admin = any(
            grupo_id in grupos_atuais and grupo_id not in novos_grupos 
            for grupo_id in admin_groups_ids
        )
        
        if removendo_admin:
            # Simular dados para validação
            dados_simulados = {'is_active': False}  # Para forçar validação
            ValidacaoSeguranca.validar_ultimo_administrador(usuario_target, dados_simulados)

class ValidacaoCompleta:
    """Classe para executar todas as validações de uma vez"""
    
    @staticmethod
    def validar_edicao_usuario(usuario_atual, usuario_target, dados):
        """Executar todas as validações para edição de usuário"""
        # 3. Não autodesativação
        ValidacaoSeguranca.validar_nao_autodesativacao(usuario_atual, usuario_target, dados)
        
        # 1. Não remover último admin
        ValidacaoSeguranca.validar_ultimo_administrador(usuario_target, dados)
        
        # 4. Hierarquia de edição
        ValidacaoSeguranca.validar_hierarquia_edicao(usuario_atual, usuario_target)
        
        # 5. Edição própria conta (limitada)
        ValidacaoSeguranca.validar_edicao_propria_conta(usuario_atual, usuario_target, dados)
        
        # 6. Grupos sensíveis
        ValidacaoSeguranca.validar_grupos_sensiveis(usuario_atual, usuario_target, dados)
    
    @staticmethod
    def validar_exclusao_usuario(usuario_atual, usuario_target):
        """Executar todas as validações para exclusão de usuário"""
        # 2. Não autoexclusão
        ValidacaoSeguranca.validar_nao_autoexclusao(usuario_atual, usuario_target)
        
        # 1. Não remover último admin
        ValidacaoSeguranca.validar_ultimo_administrador(usuario_target)
        
        # 4. Hierarquia de edição
        ValidacaoSeguranca.validar_hierarquia_edicao(usuario_atual, usuario_target)