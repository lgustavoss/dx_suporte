from rest_framework import permissions
from django.contrib.auth.models import Permission
from .models import PermissaoCustomizada

class HasCustomPermission(permissions.BasePermission):
    """
    Permissão customizada baseada no sistema de controle de acesso
    """
    def has_permission(self, request, view):
        # Usuários não autenticados não têm permissão
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuários sempre têm permissão
        if request.user.is_superuser:
            return True
        
        # Verificar se a view tem permissão customizada definida
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True  # Se não tem permissão definida, permite acesso
        
        # Verificar se o usuário tem a permissão necessária
        return self.user_has_permission(request.user, required_permission)
    
    def user_has_permission(self, user, permission_name):
        """
        Verifica se o usuário tem uma permissão específica
        """
        try:
            # Buscar permissão customizada
            perm_custom = PermissaoCustomizada.objects.get(nome=permission_name, ativo=True)
            
            # Buscar permissão do Django correspondente
            perm_django = Permission.objects.get(codename=perm_custom.nome)
            
            # Verificar se o usuário tem a permissão (diretamente ou via grupos)
            return user.has_perm(f"auth.{perm_django.codename}")
            
        except (PermissaoCustomizada.DoesNotExist, Permission.DoesNotExist):
            return False

class RequirePermission:
    """
    Decorator para definir permissões necessárias em views
    """
    def __init__(self, permission_name):
        self.permission_name = permission_name
    
    def __call__(self, view_class):
        # Adicionar permissão necessária à view
        view_class.required_permission = self.permission_name
        
        # Adicionar nossa permissão customizada às classes de permissão
        if hasattr(view_class, 'permission_classes'):
            if HasCustomPermission not in view_class.permission_classes:
                view_class.permission_classes = list(view_class.permission_classes) + [HasCustomPermission]
        else:
            view_class.permission_classes = [HasCustomPermission]
        
        return view_class

# Funções auxiliares para verificar permissões
def check_permission(user, permission_name):
    """
    Função auxiliar para verificar permissão de um usuário
    """
    permission_checker = HasCustomPermission()
    return permission_checker.user_has_permission(user, permission_name)

def get_user_permissions(user):
    """
    Retorna todas as permissões customizadas de um usuário
    """
    if user.is_superuser:
        return PermissaoCustomizada.objects.filter(ativo=True)
    
    # Buscar permissões via grupos
    user_groups = user.groups.all()
    permissions = []
    
    for group in user_groups:
        group_permissions = group.permissions.all()
        for perm in group_permissions:
            try:
                perm_custom = PermissaoCustomizada.objects.get(nome=perm.codename, ativo=True)
                permissions.append(perm_custom)
            except PermissaoCustomizada.DoesNotExist:
                pass
    
    return permissions