from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager

class GrupoCustomizado(models.Model):
    """Extensão do modelo Group do Django"""
    objects: 'Manager[GrupoCustomizado]'

    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='custom_group')
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sis_grupos'
        verbose_name = 'Grupo Customizado'
        verbose_name_plural = 'Grupos Customizados'
    
    def __str__(self):
        return f"{self.group.name}"
    
    @property
    def nome(self):
        return self.group.name
    
    @property
    def total_usuarios(self):
        return self.group.user_set.count()

    @property
    def total_permissoes(self):
        return self.group.permissions.count()

class PermissaoCustomizada(models.Model):
    """Permissões específicas do sistema (auto-descobertas)"""
    objects: 'Manager[PermissaoCustomizada]'

    modulo = models.CharField(max_length=50)
    acao = models.CharField(max_length=50)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    auto_descoberta = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ ADICIONAR
    
    class Meta:
        db_table = 'sis_permissoes'
        verbose_name = 'Permissão Customizada'
        verbose_name_plural = 'Permissões Customizadas'
        unique_together = ['modulo', 'acao']
        indexes = [
            models.Index(fields=['modulo', 'acao']),
            models.Index(fields=['nome']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{str(self.modulo).replace('_', ' ').title()} - {str(self.acao).title()}"
    
    def save(self, *args, **kwargs):
        if not self.nome:
            self.nome = f"{self.modulo}_{self.acao}"
        super().save(*args, **kwargs)
    
    @property
    def django_permission(self):
        """Obter permissão Django correspondente"""
        try:
            return Permission.objects.get(codename=self.nome)
        except Permission.DoesNotExist:
            return None

# Signals para invalidar cache
@receiver([post_save, post_delete], sender=PermissaoCustomizada)
def invalidate_permissions_cache(sender, **kwargs):
    """Invalidar cache quando permissões mudarem"""
    from .utils import invalidate_app_permissions_cache
    invalidate_app_permissions_cache()
