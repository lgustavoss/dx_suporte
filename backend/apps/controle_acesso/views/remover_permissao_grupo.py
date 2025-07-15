from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.controle_acesso.models import GrupoCustomizado
from ..permissions import HasCustomPermission, RequirePermission
from django.contrib.auth.models import Permission

@RequirePermission('controle_acesso_editar')
@extend_schema(
    summary="Remover Permissão do Grupo",
    description="Remove permissão específica de um grupo",
    tags=['Controle de Acesso'],
    responses={
        200: {'description': 'Permissão removida com sucesso'},
        404: {'description': 'Permissão ou grupo não encontrado'}
    }
)
class RemoverPermissaoGrupoView(APIView):
    permission_classes = [HasCustomPermission]
    def delete(self, request, grupo_id, permission_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permission = Permission.objects.get(id=permission_id)
            grupo_custom.group.permissions.remove(permission)
            return Response({'status': 'success','message': f'Permissão removida do grupo {grupo_custom.group.name}'})
        except (GrupoCustomizado.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
