from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Usuario(AbstractUser):
    # Campos adicionais
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    
    # Controle de status online/offline
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(blank=True, null=True)
    
    # Configurações
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'  # Login por email
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'sis_usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def set_online(self):
        """Marca usuário como online"""
        self.is_online = True
        self.last_activity = timezone.now()
        self.logout_time = None
        self.save(update_fields=['is_online', 'last_activity', 'logout_time'])
    
    def set_offline(self):
        """Marca usuário como offline"""
        self.is_online = False
        self.logout_time = timezone.now()
        self.save(update_fields=['is_online', 'logout_time'])
    
    def tempo_offline(self):
        """Retorna tempo que está offline"""
        if self.logout_time and not self.is_online:
            return timezone.now() - self.logout_time
        return None
