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
        from apps.controle_acesso.models import PermissaoCustomizada
        from apps.controle_acesso.serializers import PermissaoCustomizadaSerializer
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            # Busca os objetos Permission do grupo
            permissions = grupo_custom.group.permissions.all()
            acao_modulo_list = []
            for perm in permissions:
                codename = perm.codename
                if '_' in codename:
                    modulo, acao = codename.split('_', 1)
                    acao_modulo_list.append((acao, modulo))
            # LOG TEMPORÁRIO PARA DEBUG
            print('Codenames do grupo:', [perm.codename for perm in permissions])
            print('Pares acao/modulo extraídos:', acao_modulo_list)
            from apps.controle_acesso.models import PermissaoCustomizada
            for acao, modulo in acao_modulo_list:
                count = PermissaoCustomizada.objects.filter(acao=acao, modulo=modulo).count()
                print(f"PermissaoCustomizada(acao='{acao}', modulo='{modulo}') -> {count} encontrada(s)")
            # Busca as permissões customizadas correspondentes
            from django.db.models import Q
            q = Q()
            for acao, modulo in acao_modulo_list:
                q |= Q(acao=acao, modulo=modulo)
            permissoes_custom = PermissaoCustomizada.objects.filter(q) if acao_modulo_list else PermissaoCustomizada.objects.none()
            permissions_data = PermissaoCustomizadaSerializer(permissoes_custom, many=True).data
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
