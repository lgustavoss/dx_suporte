from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'grupos', views.GrupoViewSet, basename='grupos')
router.register(r'permissoes', views.PermissaoViewSet, basename='permissoes')

urlpatterns = [
    # CRUD grupos e permissões
    path('permissoes/sync/', views.SyncPermissoesView.as_view(), name='sync-permissoes'),
    path('', include(router.urls)),
    
    # Relacionamentos na perspectiva do GRUPO
    path('grupos/<int:grupo_id>/usuarios/', views.GrupoUsuariosView.as_view(), name='grupo-usuarios'),
    path('grupos/<int:grupo_id>/usuarios/<int:usuario_id>/', views.RemoverUsuarioGrupoView.as_view(), name='remover-usuario-grupo'),
    path('grupos/<int:grupo_id>/permissoes/', views.GrupoPermissoesView.as_view(), name='grupo-permissoes'),
    path('grupos/<int:grupo_id>/permissoes/<int:permissao_id>/', views.RemoverPermissaoGrupoView.as_view(), name='remover-permissao-grupo'),
]