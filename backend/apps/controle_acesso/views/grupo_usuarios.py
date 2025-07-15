from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.controle_acesso.models import GrupoCustomizado
from ..permissions import HasCustomPermission, RequirePermission

@RequirePermission('controle_acesso_visualizar')
@extend_schema(
    summary="Usuários do Grupo", 
    description="Gerencia usuários de um grupo específico",
    tags=['Controle de Acesso'],  
    responses={200: {'description': 'Lista de usuários do grupo'}}
)
class GrupoUsuariosView(APIView):
    permission_classes = [HasCustomPermission]
    def get(self, request, grupo_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuarios = grupo_custom.group.user_set.filter(is_active=True)
            usuarios_data = [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            } for user in usuarios]
            return Response({
                'grupo': grupo_custom.group.name,
                'usuarios': usuarios_data,
                'total': len(usuarios_data)
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, grupo_id):
        if not request.user.is_superuser:
            from ..utils import check_permission
            if not check_permission(request.user, 'controle_acesso_editar'):
                return Response({'error': 'Permissão insuficiente para editar grupos'}, status=status.HTTP_403_FORBIDDEN)
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuario_id = request.data.get('usuario_id')
            from apps.accounts.models import Usuario
            usuario = Usuario.objects.get(id=usuario_id, is_active=True)
            grupo_custom.group.user_set.add(usuario)
            return Response({'status': 'success','message': f'Usuário {usuario.username} adicionado ao grupo {grupo_custom.group.name}'})
        except (GrupoCustomizado.DoesNotExist, Usuario.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
