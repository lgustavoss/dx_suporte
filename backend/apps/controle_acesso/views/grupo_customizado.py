from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from django.contrib.auth.models import Permission
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.controle_acesso.models import GrupoCustomizado
from ..serializers import GrupoCustomizadoSerializer
from ..permissions import HasCustomPermission

@extend_schema_view(
    list=extend_schema(
        summary="Listar grupos",
        description="Lista todos os grupos customizados",
        tags=['Controle de Acesso'],  
    ),
    create=extend_schema(
        summary="Criar grupo",
        description="Cria um novo grupo customizado",
        tags=['Controle de Acesso'],  
    ),
    retrieve=extend_schema(
        summary="Detalhes do grupo",
        description="Obtém detalhes de um grupo específico",
        tags=['Controle de Acesso'],  
    ),
    update=extend_schema(
        summary="Atualizar grupo (PUT)",
        description="Substitui completamente dados do grupo",
        tags=['Controle de Acesso'],  
    ),
    partial_update=extend_schema( 
        summary="Atualizar grupo (PATCH)",
        description="Atualiza campos específicos do grupo",
        tags=['Controle de Acesso'],
    ),
    destroy=extend_schema(
        summary="Excluir grupo",
        description="Remove um grupo do sistema",
        tags=['Controle de Acesso'],  
    ),
    add_permission=extend_schema(
        summary="Adicionar Permissão ao Grupo",
        description="Adiciona uma permissão específica ao grupo",
        tags=['Controle de Acesso'],
        request={
            'type': 'object',
            'properties': {
                'permission_id': {'type': 'integer', 'description': 'ID da permissão'}
            }
        },
        responses={
            200: {'description': 'Permissão adicionada com sucesso'},
            404: {'description': 'Grupo ou permissão não encontrada'}
        }
    ),
    remove_permission=extend_schema(
        summary="Remover Permissão do Grupo",
        description="Remove uma permissão específica do grupo",
        tags=['Controle de Acesso'],
        request={
            'type': 'object',
            'properties': {
                'permission_id': {'type': 'integer', 'description': 'ID da permissão'}
            }
        },
        responses={
            200: {'description': 'Permissão removida com sucesso'},
            404: {'description': 'Grupo ou permissão não encontrada'}
        }
    ),
)
class GrupoCustomizadoViewSet(viewsets.ModelViewSet):
    def destroy(self, request, *args, **kwargs):
        grupo = self.get_object()
        user = request.user
        # Exclusão definitiva só para superuser ou admin
        if not user.is_superuser:
            # Verifica se está em grupo admin
            admin_groups = user.groups.filter(name__icontains='admin')
            if not admin_groups.exists():
                return Response({'detail': 'Apenas administradores podem excluir grupos.'}, status=status.HTTP_403_FORBIDDEN)
        # Só permite exclusão se não houver usuários vinculados
        if grupo.total_usuarios > 0:
            return Response({'detail': 'Não é possível excluir grupos com usuários vinculados.'}, status=status.HTTP_400_BAD_REQUEST)
        grupo.delete()
        return Response({'detail': 'Grupo excluído com sucesso.'}, status=status.HTTP_204_NO_CONTENT)
    """ViewSet para gerenciar grupos customizados"""
    queryset = GrupoCustomizado.objects.all()
    serializer_class = GrupoCustomizadoSerializer
    permission_classes = [HasCustomPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['group__name', 'descricao']
    filterset_fields = ['group__name']
    ordering_fields = ['group__name', 'created_at']
    ordering = ['group__name']
    def get_permissions(self):
        self.permission_required = 'controle_acesso_gerenciar'
        return [HasCustomPermission()]
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        permission_checker = HasCustomPermission()
        return permission_checker.user_has_permission(request.user, 'controle_acesso_gerenciar')
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        grupo = self.get_object()
        permission_id = request.data.get('permission_id')
        try:
            # Sincroniza customizada e Django
            from apps.controle_acesso.models import PermissaoCustomizada
            perm_custom = PermissaoCustomizada.objects.filter(id=permission_id).first()
            if not perm_custom:
                return Response({
                    'status': 'error',
                    'message': 'Permissão customizada não encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
            perm_django = Permission.objects.filter(codename=perm_custom.nome).first()
            if not perm_django:
                return Response({
                    'status': 'error',
                    'message': 'Permissão Django não encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
            grupo.group.permissions.add(perm_django)
            return Response({
                'status': 'success',
                'message': f'Permissão {perm_custom.nome} adicionada ao grupo {grupo.group.name}'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['delete'])
    def remove_permission(self, request, pk=None):
        grupo = self.get_object()
        permission_id = request.data.get('permission_id')
        try:
            from apps.controle_acesso.models import PermissaoCustomizada
            perm_custom = PermissaoCustomizada.objects.filter(id=permission_id).first()
            if not perm_custom:
                return Response({
                    'status': 'error',
                    'message': 'Permissão customizada não encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
            perm_django = Permission.objects.filter(codename=perm_custom.nome).first()
            if not perm_django:
                return Response({
                    'status': 'error',
                    'message': 'Permissão Django não encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
            grupo.group.permissions.remove(perm_django)
            return Response({
                'status': 'success',
                'message': f'Permissão {perm_custom.nome} removida do grupo {grupo.group.name}'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
