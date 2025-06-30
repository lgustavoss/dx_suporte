from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings  # ✅ ADICIONAR IMPORT
from .models import PermissaoCustomizada


class HasCustomPermission(BasePermission):
    """
    Classe para verificação de permissões customizadas
    """
    
    def has_permission(self, request, view):
        # ✅ CRÍTICO: Verificar autenticação primeiro
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ✅ CRÍTICO: Superuser sempre tem acesso
        if request.user.is_superuser:
            return True
        
        # ✅ OBTER PERMISSÃO REQUERIDA DA VIEW
        permission_required = getattr(view, 'permission_required', None)
        
        # ✅ CASOS ESPECIAIS: Views que não precisam de permissão específica
        special_views = [
            'status-online',  # ← Endpoint de status
            'minhas-permissoes'  # ← Endpoint de permissões do usuário
        ]
        
        # Verificar se é uma view especial pelo nome da ação ou URL
        view_name = getattr(view, 'action', None) or getattr(view, 'basename', '')
        if any(special in view_name.lower() for special in special_views):
            return True  # ← Permitir acesso apenas com autenticação
        
        # ✅ MUDANÇA: Se não há permissão definida, NEGAR acesso (mais seguro)
        if not permission_required:
            return False
        
        # ✅ VERIFICAR PERMISSÃO
        return self.user_has_permission(request.user, permission_required)
    
    def user_has_permission(self, user, permission_name):
        """
        ✅ VERIFICAR se usuário tem permissão específica
        """
        # Superuser bypass
        if user.is_superuser:
            return True
        
        try:
            # ✅ VERIFICAR se existe permissão customizada ATIVA
            perm_custom = PermissaoCustomizada.objects.get(
                nome=permission_name, 
                ativo=True
            )
            
            # ✅ CORRIGIR: Filtrar permissões Django por app correto
            try:
                # Determinar app_label baseado no módulo da permissão customizada
                app_label = perm_custom.modulo
                
                # ✅ BUSCAR permissão Django específica do app
                perm_django = Permission.objects.filter(
                    codename=permission_name,
                    content_type__app_label=app_label
                ).first()  # ← Usar .first() ao invés de .get()
                
                if not perm_django:
                    # Se não existe permissão Django, NEGAR
                    return False
                
                # ✅ VERIFICAR permissão real do usuário
                full_permission = f"{app_label}.{permission_name}"
                has_perm = user.has_perm(full_permission)
                
                # ✅ DEBUG CONDICIONAL (removido em produção)
                if getattr(settings, 'DEBUG_PERMISSIONS', False):
                    print(f"=== DEBUG PERMISSION ===")
                    print(f"User: {user.username}")
                    print(f"Permission: {permission_name}")
                    print(f"App label: {app_label}")
                    print(f"Full permission: {full_permission}")
                    print(f"User permissions: {list(user.get_all_permissions())}")
                    print(f"Has permission: {has_perm}")
                    print(f"=== END DEBUG ===")
                
                return has_perm
                
            except Exception as e:
                # ✅ Log do erro para debug (sem settings)
                print(f"Erro ao verificar permissão {permission_name}: {e}")
                return False
                
        except PermissaoCustomizada.DoesNotExist:
            # ✅ Se não existe permissão customizada, NEGAR
            return False


def check_permission(user, permission_name):
    """
    ✅ CORRIGIDO: Função standalone para verificar permissões
    Usar a mesma lógica da classe principal para consistência
    """
    permission_checker = HasCustomPermission()
    return permission_checker.user_has_permission(user, permission_name)


class RequirePermission:
    """
    ✅ CORRIGIDO: Decorator para aplicar permissões em views
    """
    def __init__(self, permission_name):
        self.permission_name = permission_name
    
    def __call__(self, view_class):
        # ✅ CRÍTICO: Aplicar permissão a TODOS os métodos da classe
        view_class.permission_required = self.permission_name
        
        # ✅ FORÇAR: Sobrescrever permission_classes completamente
        view_class.permission_classes = [HasCustomPermission]
        
        # ✅ CRÍTICO: Sobrescrever get_permissions para garantir aplicação
        def get_permissions(self):
            """Garantir que sempre usa HasCustomPermission"""
            self.permission_required = view_class.permission_required  # ← CORRIGIDO
            
            # Retornar sempre nossa classe de permissão
            return [HasCustomPermission()]
        
        view_class.get_permissions = get_permissions
        
        return view_class