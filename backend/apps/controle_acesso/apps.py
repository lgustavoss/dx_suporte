from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ControleAcessoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controle_acesso'
    verbose_name = 'Controle de Acesso'
    
    def ready(self):
        """Conectar signals quando app estiver pronto"""
        from django.contrib.auth.models import Permission
        
        def sync_permissions_after_migrate(sender, **kwargs):
            """Sincronizar permissões após migrations"""
            # Só executar para este app
            if kwargs.get('app_config') == self:
                from .utils import sync_permissions
                try:
                    created_count = sync_permissions()
                    if created_count > 0:
                        print(f"✅ {created_count} permissões sincronizadas automaticamente")
                except Exception as e:
                    print(f"⚠️ Erro na sincronização automática: {e}")
        
        # Conectar signal
        post_migrate.connect(sync_permissions_after_migrate, sender=self)
