from django.apps import apps
from django.conf import settings

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
    from .models import PermissaoCustomizada
    
    discovered_permissions = get_app_permissions()
    created_count = 0
    
    for perm_data in discovered_permissions:
        perm, created = PermissaoCustomizada.objects.get_or_create(
            nome=perm_data['nome'],
            defaults={
                'modulo': perm_data['modulo'],
                'acao': perm_data['acao'],
                'descricao': f"Permissão para {perm_data['acao']} em {perm_data['modulo_display']}",
                'auto_descoberta': True
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ {created_count} novas permissões criadas! Total descoberto: {len(discovered_permissions)}")
    return created_count