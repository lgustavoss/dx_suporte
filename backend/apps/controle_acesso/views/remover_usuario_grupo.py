from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.controle_acesso.models import GrupoCustomizado
from ..permissions import HasCustomPermission, RequirePermission
from apps.accounts.models import Usuario

@RequirePermission('controle_acesso_editar')
@extend_schema(
    summary="Remover Usuário do Grupo",
    description="Remove usuário específico de um grupo",
    tags=['Controle de Acesso'],
    responses={
        200: {'description': 'Usuário removido com sucesso'},
        404: {'description': 'Usuário ou grupo não encontrado'}
    }
)
class RemoverUsuarioGrupoView(APIView):
    permission_classes = [HasCustomPermission]
    def delete(self, request, grupo_id, usuario_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuario = Usuario.objects.get(id=usuario_id)
            grupo_custom.group.user_set.remove(usuario)
            return Response({'status': 'success','message': f'Usuário {usuario.username} removido do grupo {grupo_custom.group.name}'})
        except (GrupoCustomizado.DoesNotExist, Usuario.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
