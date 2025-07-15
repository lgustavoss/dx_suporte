from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views.grupo_detalhe import GrupoDetalheViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'permissoes', views.PermissaoCustomizadaViewSet, basename='permissoes')
router.register(r'grupos-detalhe', GrupoDetalheViewSet, basename='grupos-detalhe')
router.register(r'grupos', views.GrupoCustomizadoViewSet, basename='grupos')

urlpatterns = [
    # URL de Sincronização de Permissões
    path('sync-permissoes/', views.SyncPermissoesView.as_view(), name='sync-permissoes'),
    
    # Router URLs
    path('', include(router.urls)),
    
    # Grupos e permissões
    path('grupos/<int:grupo_id>/usuarios/', views.GrupoUsuariosView.as_view(), name='grupo-usuarios'),
    path('grupos/<int:grupo_id>/usuarios/<int:usuario_id>/', views.RemoverUsuarioGrupoView.as_view(), name='remover-usuario-grupo'),
    path('grupos/<int:grupo_id>/permissoes/', views.GrupoPermissoesView.as_view(), name='grupo-permissoes'),
    path('grupos/<int:grupo_id>/permissoes/<int:permissao_id>/', views.RemoverPermissaoGrupoView.as_view(), name='remover-permissao-grupo'),
    
    # Teste de permissões
    path('test-permissions/', views.TestPermissionsView.as_view(), name='test-permissions'),
]