from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

Usuario = get_user_model()

class PermissionAuditLog(models.Model):
    """Log de auditoria para mudanças em permissões"""
    
    ACTIONS = [
        ('GRANT', 'Permissão Concedida'),
        ('REVOKE', 'Permissão Revogada'),
        ('CREATE', 'Permissão Criada'),
        ('DELETE', 'Permissão Deletada'),
        ('SYNC', 'Sincronização de Permissões'),
    ]
    
    user = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTIONS)
    permission_name = models.CharField(max_length=100)
    target_user = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='permission_logs_as_target'
    )
    group_name = models.CharField(max_length=150, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'permission_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['permission_name', '-timestamp']),
            models.Index(fields=['target_user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.permission_name} - {self.timestamp}"

def log_permission_change(action, permission_name, user=None, target_user=None, 
                         group_name=None, details=None, request=None):
    """
    Registrar mudança de permissão
    """
    ip_address = None
    if request:
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    
    PermissionAuditLog.objects.create(
        user=user,
        action=action,
        permission_name=permission_name,
        target_user=target_user,
        group_name=group_name,
        details=details or {},
        ip_address=ip_address
    )