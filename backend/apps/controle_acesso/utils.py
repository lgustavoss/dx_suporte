from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.controle_acesso.models import PermissaoCustomizada
from django.core.cache import cache
import hashlib

# Cache keys
CACHE_KEY_USER_PERMISSIONS = 'user_permissions_{user_id}'
CACHE_KEY_APP_PERMISSIONS = 'app_permissions'
CACHE_TIMEOUT = getattr(settings, 'PERMISSIONS_CACHE_TIMEOUT', 300)  # 5 minutos

def get_app_permissions():
    """Descobre automaticamente permissões dos apps instalados"""
    permissions = []
    
    # Buscar configurações do controle de acesso
    controle_config = getattr(settings, 'CONTROLE_ACESSO', {})
    skip_apps = controle_config.get('SKIP_APPS', ['endpoints'])
    acoes_default = controle_config.get('ACOES_DEFAULT', ['criar', 'visualizar', 'editar', 'excluir'])
    
    # Apps customizados (que estão em INSTALLED_APPS)
    custom_apps = [app for app in settings.INSTALLED_APPS 
                   if not app.startswith('django.') 
                   and not app.startswith('rest_framework')]
    
    for app_name in custom_apps:
        if app_name in skip_apps:
            continue
            
        try:
            app_config = apps.get_app_config(app_name)
            display_name = getattr(app_config, 'verbose_name', app_name.replace('_', ' ').title())
            
            for acao in acoes_default:
                permissions.append({
                    'modulo': app_name,
                    'modulo_display': display_name,
                    'acao': acao,
                    'nome': f"{app_name}_{acao}"
                })
        except Exception as e:
            # Se app não existe, skip
            continue
    
    return permissions

def sync_permissions():
    """Sincroniza permissões automaticamente"""
    created_count = 0
    
    # ✅ DESCOBRIR permissões dos apps primeiro
    app_permissions = get_app_permissions()
    
    # Criar permissões customizadas se não existirem
    for perm_data in app_permissions:
        perm_custom, created = PermissaoCustomizada.objects.get_or_create(
            nome=perm_data['nome'],
            defaults={
                'modulo': perm_data['modulo'],
                'acao': perm_data['acao'],
                'descricao': f"{perm_data['acao'].title()} {perm_data['modulo_display']}",
                'auto_descoberta': True,
                'ativo': True
            }
        )
        
        if created:
            created_count += 1
    
    # ✅ CRÍTICO: Criar permissões Django correspondentes SEM DUPLICATAS
    perms_customizadas = PermissaoCustomizada.objects.filter(ativo=True)
    
    for perm_custom in perms_customizadas:
        try:
            # ✅ VERIFICAR se existe permissão Django para este app específico
            app_label = perm_custom.modulo
            
            # Determinar content_type baseado no módulo
            if app_label == 'accounts':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                content_type = ContentType.objects.get_for_model(User)
            elif app_label == 'controle_acesso':
                content_type = ContentType.objects.get_for_model(PermissaoCustomizada)
            else:
                # Content type genérico para outros módulos
                from django.contrib.auth.models import Group
                content_type = ContentType.objects.get_for_model(Group)
            
            # ✅ CRÍTICO: USAR get_or_create para evitar duplicatas
            perm_django, created = Permission.objects.get_or_create(
                codename=perm_custom.nome,
                content_type=content_type,
                defaults={
                    'name': perm_custom.descricao or f"{perm_custom.acao} {perm_custom.modulo}"
                }
            )
            
            if created:
                created_count += 1
                
        except Exception as e:
            print(f"❌ Erro ao criar permissão Django {perm_custom.nome}: {e}")
    
    return created_count


def check_permission(user, permission_name):
    """
    Verificar se usuário tem permissão específica
    """
    # Superuser sempre tem acesso
    if user.is_superuser:
        return True
    
    # Verificar se usuário está autenticado
    if not user.is_authenticated:
        return False
    
    try:
        # ✅ Buscar permissão customizada ativa
        perm_customizada = PermissaoCustomizada.objects.get(
            nome=permission_name,
            ativo=True
        )
        
        # ✅ Buscar permissão Django correspondente
        from django.contrib.auth.models import Permission
        django_perm = Permission.objects.filter(
            codename=permission_name
        ).first()
        
        if not django_perm:
            return False
        
        # ✅ VERIFICAR: Permissão direta do usuário
        if user.user_permissions.filter(id=django_perm.id).exists():
            return True
        
        # ✅ VERIFICAR: Permissão via grupos
        if user.groups.filter(permissions=django_perm).exists():
            return True
        
        return False
        
    except PermissaoCustomizada.DoesNotExist:
        return False
    except Exception as e:
        # ✅ CORRIGIR: Importar DEBUG_PERMISSIONS
        DEBUG_PERMISSIONS = getattr(settings, 'DEBUG_PERMISSIONS', False)
        if DEBUG_PERMISSIONS:
            print(f"DEBUG check_permission error: {e}")
        return False


def get_user_permissions(user):
    """
    Obter todas as permissões customizadas do usuário
    """
    if user.is_superuser:
        # Superuser tem todas as permissões ativas
        return PermissaoCustomizada.objects.filter(ativo=True)
    
    # Obter permissões Django do usuário
    user_perms = user.get_all_permissions()
    
    # Extrair apenas os codenames
    codenames = [perm.split('.')[1] for perm in user_perms if '.' in perm]
    
    # Filtrar permissões customizadas correspondentes
    return PermissaoCustomizada.objects.filter(
        nome__in=codenames,
        ativo=True
    )


def has_any_permission(user, permission_list):
    """
    ✅ NOVO: Verificar se usuário tem qualquer uma das permissões da lista
    """
    if user.is_superuser:
        return True
    
    for permission_name in permission_list:
        if check_permission(user, permission_name):
            return True
    
    return False


def require_permissions(permission_list, require_all=True):
    """
    ✅ NOVO: Decorator para múltiplas permissões
    
    Args:
        permission_list: Lista de permissões
        require_all: Se True, usuário deve ter TODAS. Se False, pelo menos UMA.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                from django.http import JsonResponse
                return JsonResponse({'error': 'Não autenticado'}, status=401)
            
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if require_all:
                # Usuário deve ter TODAS as permissões
                for perm in permission_list:
                    if not check_permission(user, perm):
                        from django.http import JsonResponse
                        return JsonResponse({'error': f'Permissão negada: {perm}'}, status=403)
            else:
                # Usuário deve ter PELO MENOS UMA permissão
                if not has_any_permission(user, permission_list):
                    from django.http import JsonResponse
                    return JsonResponse({'error': 'Acesso negado'}, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def get_user_permissions_cached(user):
    """
    Obter permissões do usuário com cache
    """
    if user.is_superuser:
        # Superuser sempre tem todas as permissões, não precisa cache
        return PermissaoCustomizada.objects.filter(ativo=True)
    
    cache_key = CACHE_KEY_USER_PERMISSIONS.format(user_id=user.id)
    permissions = cache.get(cache_key)
    
    if permissions is None:
        # Calcular permissões
        user_perms = user.get_all_permissions()
        codenames = [perm.split('.')[1] for perm in user_perms if '.' in perm]
        
        permissions = list(PermissaoCustomizada.objects.filter(
            nome__in=codenames,
            ativo=True
        ).values('nome', 'descricao', 'modulo', 'acao'))
        
        # Cache por 5 minutos
        cache.set(cache_key, permissions, CACHE_TIMEOUT)
    
    return permissions

def invalidate_user_permissions_cache(user):
    """Invalidar cache de permissões do usuário"""
    cache_key = CACHE_KEY_USER_PERMISSIONS.format(user_id=user.id)
    cache.delete(cache_key)

def get_app_permissions_cached():
    """
    Obter permissões dos apps com cache
    """
    permissions = cache.get(CACHE_KEY_APP_PERMISSIONS)
    
    if permissions is None:
        permissions = get_app_permissions()
        # Cache por 1 hora (permissões de apps mudam raramente)
        cache.set(CACHE_KEY_APP_PERMISSIONS, permissions, 3600)
    
    return permissions

def invalidate_app_permissions_cache():
    """Invalidar cache de permissões dos apps"""
    cache.delete(CACHE_KEY_APP_PERMISSIONS)