from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from ..permissions import HasCustomPermission, RequirePermission

@extend_schema(
    summary="Sincronizar Permissões",
    description="Sincroniza automaticamente todas as permissões do sistema",
    tags=['Controle de Acesso'],  
    request=None,
    responses={200: {'description': 'Permissões sincronizadas com sucesso'}}
)
@RequirePermission('controle_acesso_gerenciar')
class SyncPermissoesView(APIView):
    permission_classes = [HasCustomPermission]
    def post(self, request):
        try:
            from ..utils import sync_permissions
            created_count = sync_permissions()
            return Response({
                'status': 'success',
                'message': f'✅ {created_count} permissões sincronizadas com sucesso!',
                'created_count': created_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'❌ Erro ao sincronizar permissões: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
