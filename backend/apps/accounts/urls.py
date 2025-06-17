from django.urls import path, include  # ← Adicionado 'include'
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, 
    logout_view, 
    status_online_view,
    UsuarioViewSet,
    UsuarioGruposView,
    minhas_permissoes_view 
)
from rest_framework.routers import DefaultRouter

# Router para usuários
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    # Autenticação JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    
    # Status online/offline
    path('status-online/', status_online_view, name='status_online'),
    
    # CRUD usuários
    path('', include(router.urls)),
    
    # Relacionamentos na perspectiva do USUÁRIO
    path('usuarios/<int:usuario_id>/grupos/', UsuarioGruposView.as_view(), name='usuario-grupos'),
    
    # Permissões do usuário autenticado
    path('minhas-permissoes/', minhas_permissoes_view, name='minhas-permissoes'),
]