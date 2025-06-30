from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def auto_sync_permissions(sender, **kwargs):
    """
    Sincronizar permissões automaticamente após migrations
    """
    # Verificar se auto-sync está habilitado
    controle_config = getattr(settings, 'CONTROLE_ACESSO', {})
    auto_sync = controle_config.get('AUTO_SYNC_AFTER_MIGRATE', False)
    
    if not auto_sync:
        return
    
    # Só executar para apps relacionados ao controle de acesso
    if sender.name in ['controle_acesso', 'accounts']:
        try:
            logger.info(f"🔄 Auto-sincronizando permissões após migração do app: {sender.name}")
            call_command('sync_permissions', verbosity=0)
            logger.info("✅ Auto-sincronização de permissões concluída")
        except Exception as e:
            logger.error(f"❌ Erro na auto-sincronização de permissões: {e}")