from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.controle_acesso.models import GrupoCustomizado
from ..permissions import HasCustomPermission, RequirePermission
from django.contrib.auth.models import Permission

@RequirePermission('controle_acesso_visualizar')
@extend_schema(
    summary="Permissões do Grupo",
    description="Gerencia permissões de um grupo específico",
    tags=['Controle de Acesso'],  
    responses={200: {'description': 'Lista de permissões do grupo'}}
)
class GrupoPermissoesView(APIView):
    permission_classes = [HasCustomPermission]
    def get(self, request, grupo_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permissions = grupo_custom.group.permissions.all()
            permissions_data = [{
                'id': perm.id,
                'codename': perm.codename,
                'name': perm.name,
                'content_type': perm.content_type.model
            } for perm in permissions]
            return Response({
                'grupo': grupo_custom.group.name,
                'permissions': permissions_data
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, grupo_id):
        if not self.request.user.is_superuser:
            from ..utils import check_permission
            if not check_permission(request.user, 'controle_acesso_editar'):
                return Response({'error': 'Permissão insuficiente para editar grupos'}, status=status.HTTP_403_FORBIDDEN)
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permission_id = request.data.get('permission_id')
            permission = Permission.objects.get(id=permission_id)
            grupo_custom.group.permissions.add(permission)
            return Response({'status': 'success','message': f'Permissão adicionada ao grupo {grupo_custom.group.name}'})
        except (GrupoCustomizado.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, grupo_id):
        if not self.request.user.is_superuser:
            from ..utils import check_permission
            if not check_permission(request.user, 'controle_acesso_editar'):
                return Response({'error': 'Permissão insuficiente para editar grupos'}, status=status.HTTP_403_FORBIDDEN)
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permission_id = request.data.get('permission_id')
            permission = Permission.objects.get(id=permission_id)
            grupo_custom.group.permissions.remove(permission)
            return Response({'status': 'success','message': f'Permissão removida do grupo {grupo_custom.group.name}'})
        except (GrupoCustomizado.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
