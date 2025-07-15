from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Group
from apps.accounts.models import Usuario
from apps.controle_acesso.models import PermissaoCustomizada
from apps.controle_acesso.serializers import PermissaoCustomizadaSerializer
from apps.accounts.serializers import UsuarioSerializer
from rest_framework.permissions import IsAuthenticated

class GrupoDetalheViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        try:
            grupo = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({'detail': 'Grupo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        permissoes = PermissaoCustomizada.objects.filter(groups=grupo)
        usuarios = Usuario.objects.filter(groups=grupo)
        return Response({
            'id': grupo.id,
            'name': grupo.name,
            'permissoes': PermissaoCustomizadaSerializer(permissoes, many=True).data,
            'usuarios': UsuarioSerializer(usuarios, many=True).data,
        })

    @action(detail=True, methods=['post'])
    def add_usuario(self, request, pk=None):
        grupo = Group.objects.get(pk=pk)
        user_id = request.data.get('user_id')
        try:
            user = Usuario.objects.get(pk=user_id)
            user.groups.add(grupo)
            return Response({'detail': 'Usuário adicionado.'})
        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_usuario(self, request, pk=None):
        grupo = Group.objects.get(pk=pk)
        user_id = request.data.get('user_id')
        try:
            user = Usuario.objects.get(pk=user_id)
            user.groups.remove(grupo)
            return Response({'detail': 'Usuário removido.'})
        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def add_permissao(self, request, pk=None):
        grupo = Group.objects.get(pk=pk)
        perm_id = request.data.get('perm_id')
        try:
            perm = PermissaoCustomizada.objects.get(pk=perm_id)
            perm.groups.add(grupo)
            return Response({'detail': 'Permissão adicionada.'})
        except PermissaoCustomizada.DoesNotExist:
            return Response({'detail': 'Permissão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_permissao(self, request, pk=None):
        grupo = Group.objects.get(pk=pk)
        perm_id = request.data.get('perm_id')
        try:
            perm = PermissaoCustomizada.objects.get(pk=perm_id)
            perm.groups.remove(grupo)
            return Response({'detail': 'Permissão removida.'})
        except PermissaoCustomizada.DoesNotExist:
            return Response({'detail': 'Permissão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
