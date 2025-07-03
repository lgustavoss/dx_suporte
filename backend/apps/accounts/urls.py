from django.urls import path, include
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,  # ✅ ADICIONAR NOVA VIEW
    logout_view,
    status_online,
    UsuarioViewSet,
    UsuarioGruposView,
    MinhasPermissoesView,
    me_view,
)
from rest_framework.routers import DefaultRouter

# Router para usuários
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    # ✅ Autenticação JWT - TODOS com tags 'Autenticação'
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),

    # ✅ ADICIONAR: Endpoint para dados do usuário atual
    path('usuarios/me/', me_view, name='usuarios-me'),
    
    # ✅ Status online/offline - tag 'Utilitários'
    path('status-online/', status_online, name='status_online'),
    
    # ✅ CRUD usuários - todas as actions com tag 'Usuários'
    path('', include(router.urls)),
    
    # ✅ Relacionamentos - tag 'Usuários'
    path('usuarios/<int:usuario_id>/grupos/', UsuarioGruposView.as_view(), name='usuario-grupos'),
    
    # ✅ Permissões do usuário autenticado - tag 'Utilitários'
    path('minhas-permissoes/', MinhasPermissoesView.as_view(), name='minhas-permissoes'),
]