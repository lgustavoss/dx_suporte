from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'permissoes', views.PermissaoCustomizadaViewSet, basename='permissoes')
router.register(r'grupos-customizados', views.GrupoCustomizadoViewSet, basename='grupos-customizados')

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