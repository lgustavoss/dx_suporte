from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..permissions import HasCustomPermission, RequirePermission

@RequirePermission('controle_acesso_visualizar')
@extend_schema(
    summary="Testar Permissões do Usuário",
    description="Endpoint para testar sistema de permissões do usuário atual",
    tags=['Utilitários'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'user': {'type': 'string'},
                'is_superuser': {'type': 'boolean'},
                'permissions_count': {'type': 'integer'},
                'permissions': {'type': 'array'}
            }
        }
    }
)
class TestPermissionsView(APIView):
    permission_classes = [HasCustomPermission]
    def get(self, request):
        from ..utils import get_user_permissions
        user_permissions = get_user_permissions(request.user)
        return Response({
            'user': request.user.username,
            'is_superuser': request.user.is_superuser,
            'permissions_count': user_permissions.count(),
            'permissions': [
                {
                    'nome': perm.nome,
                    'descricao': perm.descricao,
                    'ativo': perm.ativo,
                    'modulo': perm.modulo,
                    'acao': perm.acao
                }
                for perm in user_permissions[:10]
            ]
        })
