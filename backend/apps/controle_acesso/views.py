from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import PermissaoCustomizada, GrupoCustomizado
from .serializers import PermissaoCustomizadaSerializer, GrupoCustomizadoSerializer
from .permissions import HasCustomPermission, RequirePermission

# Verifica se a classe GlobalSearchFilter existe
try:
    from core.filters import GlobalSearchFilter
except ImportError:
    # Se não existir, criar uma classe vazia
    class GlobalSearchFilter:
        pass


@extend_schema_view(
    list=extend_schema(
        summary="Listar permissões",
        description="Lista todas as permissões customizadas",
        tags=['Controle de Acesso'],  
    ),
    create=extend_schema(
        summary="Criar permissão",
        description="Cria uma nova permissão customizada",
        tags=['Controle de Acesso'],  
    ),
    retrieve=extend_schema(
        summary="Detalhes da permissão",
        description="Obtém detalhes de uma permissão específica",
        tags=['Controle de Acesso'],  
    ),
    update=extend_schema(
        summary="Atualizar permissão (PUT)",
        description="Substitui completamente dados da permissão",
        tags=['Controle de Acesso'],  
    ),
    partial_update=extend_schema(
        summary="Atualizar permissão (PATCH)",
        description="Atualiza campos específicos da permissão",
        tags=['Controle de Acesso'],
    ),
    destroy=extend_schema(
        summary="Excluir permissão",
        description="Remove uma permissão do sistema",
        tags=['Controle de Acesso'],  
    ),
)
class PermissaoCustomizadaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar permissões customizadas"""
    
    queryset = PermissaoCustomizada.objects.all()
    serializer_class = PermissaoCustomizadaSerializer
    
    # ✅ DEFINIR permission_classes SEMPRE
    permission_classes = [HasCustomPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao', 'modulo', 'acao']
    filterset_fields = ['modulo', 'acao', 'ativo']
    ordering_fields = ['nome', 'modulo', 'created_at']
    ordering = ['nome']
    
    def get_permissions(self):
        """Definir permissões baseadas na action"""
        # ✅ DEFINIR permissão específica para cada action
        if self.action == 'list':
            self.permission_required = 'controle_acesso_visualizar'
        elif self.action == 'retrieve':
            self.permission_required = 'controle_acesso_visualizar'
        elif self.action == 'create':
            self.permission_required = 'controle_acesso_criar'
        elif self.action in ['update', 'partial_update']:
            self.permission_required = 'controle_acesso_editar'
        elif self.action == 'destroy':
            self.permission_required = 'controle_acesso_excluir'
        else:
            # ✅ SEGURANÇA: Actions não definidas requerem gerenciar
            self.permission_required = 'controle_acesso_gerenciar'
        
        return [HasCustomPermission()]


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
    
    # ✅ ADICIONAR: Tags para actions customizadas
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
        """Definir permissões baseadas na action"""
        self.permission_required = 'controle_acesso_gerenciar'
        return [HasCustomPermission()]
    
    def has_permission(self, request, view):
        """Método adicional para garantir verificação"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        permission_checker = HasCustomPermission()
        return permission_checker.user_has_permission(request.user, 'controle_acesso_gerenciar')
    
    # ✅ MANTER: Actions customizadas já existentes
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Adicionar permissão a um grupo"""
        grupo = self.get_object()
        permission_id = request.data.get('permission_id')
        
        try:
            permission = Permission.objects.get(id=permission_id)
            grupo.group.permissions.add(permission)
            
            return Response({
                'status': 'success',
                'message': f'Permissão {permission.name} adicionada ao grupo {grupo.group.name}'
            })
        except Permission.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Permissão não encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_permission(self, request, pk=None):
        """Remover permissão de um grupo"""
        grupo = self.get_object()
        permission_id = request.data.get('permission_id')
        
        try:
            permission = Permission.objects.get(id=permission_id)
            grupo.group.permissions.remove(permission)
            
            return Response({
                'status': 'success',
                'message': f'Permissão {permission.name} removida do grupo {grupo.group.name}'
            })
        except Permission.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Permissão não encontrada'
            }, status=status.HTTP_404_NOT_FOUND)


@RequirePermission('controle_acesso_visualizar')
@extend_schema(
    summary="Permissões do Grupo",
    description="Gerencia permissões de um grupo específico",
    tags=['Controle de Acesso'],  
    responses={200: {'description': 'Lista de permissões do grupo'}}
)
class GrupoPermissoesView(APIView):
    """✅ CORRIGIDO: Gerenciar permissões em grupos com permissão específica"""
    permission_classes = [HasCustomPermission]
    
    def get(self, request, grupo_id):
        """Listar permissões de um grupo"""
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
            return Response({
                'error': 'Grupo não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, grupo_id):
        """Adicionar permissão a um grupo"""
        # ✅ VERIFICAÇÃO: Só permitir POST com permissão de editar
        if not self.request.user.is_superuser:
            from .utils import check_permission
            if not check_permission(request.user, 'controle_acesso_editar'):
                return Response({
                    'error': 'Permissão insuficiente para editar grupos'
                }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permission_id = request.data.get('permission_id')
            
            permission = Permission.objects.get(id=permission_id)
            grupo_custom.group.permissions.add(permission)
            
            return Response({
                'status': 'success',
                'message': f'Permissão adicionada ao grupo {grupo_custom.group.name}'
            })
        except (GrupoCustomizado.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, grupo_id):
        """Remover permissão de um grupo"""
        # ✅ VERIFICAÇÃO: Só permitir DELETE com permissão de editar
        if not self.request.user.is_superuser:
            from .utils import check_permission
            if not check_permission(request.user, 'controle_acesso_editar'):
                return Response({
                    'error': 'Permissão insuficiente para editar grupos'
                }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permission_id = request.data.get('permission_id')
            
            permission = Permission.objects.get(id=permission_id)
            grupo_custom.group.permissions.remove(permission)
            
            return Response({
                'status': 'success',
                'message': f'Permissão removida do grupo {grupo_custom.group.name}'
            })
        except (GrupoCustomizado.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


# ✅ NOVA VIEW: Para testar o sistema de permissões
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
    """View para testar o sistema de permissões"""
    permission_classes = [HasCustomPermission]
    
    def get(self, request):
        """Testar permissões do usuário atual"""
        from .utils import get_user_permissions
        
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
                for perm in user_permissions[:10]  # Primeiras 10
            ]
        })


@extend_schema(
    summary="Sincronizar Permissões",
    description="Sincroniza automaticamente todas as permissões do sistema",
    tags=['Controle de Acesso'],  
    request=None,
    responses={200: {'description': 'Permissões sincronizadas com sucesso'}}
)
@RequirePermission('controle_acesso_gerenciar')
class SyncPermissoesView(APIView):
    """View para sincronizar permissões automaticamente"""
    permission_classes = [HasCustomPermission]
    
    def post(self, request):
        """Sincronizar permissões do sistema"""
        try:
            from .utils import sync_permissions
            
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


# Views auxiliares que também podem estar faltando
@RequirePermission('controle_acesso_visualizar')
@extend_schema(
    summary="Usuários do Grupo", 
    description="Gerencia usuários de um grupo específico",
    tags=['Controle de Acesso'],  
    responses={200: {'description': 'Lista de usuários do grupo'}}
)
class GrupoUsuariosView(APIView):
    """View para gerenciar usuários em grupos"""
    permission_classes = [HasCustomPermission]
    
    def get(self, request, grupo_id):
        """Listar usuários de um grupo"""
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
            return Response({
                'error': 'Grupo não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, grupo_id):
        """Adicionar usuário a um grupo"""
        # Verificar permissão de edição
        if not request.user.is_superuser:
            from .utils import check_permission
            if not check_permission(request.user, 'controle_acesso_editar'):
                return Response({
                    'error': 'Permissão insuficiente para editar grupos'
                }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuario_id = request.data.get('usuario_id')
            
            from accounts.models import Usuario
            usuario = Usuario.objects.get(id=usuario_id, is_active=True)
            
            grupo_custom.group.user_set.add(usuario)
            
            return Response({
                'status': 'success',
                'message': f'Usuário {usuario.username} adicionado ao grupo {grupo_custom.group.name}'
            })
        except (GrupoCustomizado.DoesNotExist, Usuario.DoesNotExist) as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


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
    """View para remover usuário de um grupo"""
    permission_classes = [HasCustomPermission]
    
    def delete(self, request, grupo_id, usuario_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Remover usuário do grupo Django
            grupo_custom.group.user_set.remove(usuario)
            
            return Response({
                'status': 'success',
                'message': f'Usuário {usuario.username} removido do grupo {grupo_custom.group.name}'
            })
        except (GrupoCustomizado.DoesNotExist, Usuario.DoesNotExist) as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


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
    """View para remover permissão de um grupo"""
    permission_classes = [HasCustomPermission]
    
    def delete(self, request, grupo_id, permission_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permission = Permission.objects.get(id=permission_id)
            
            # Remover permissão do grupo Django
            grupo_custom.group.permissions.remove(permission)
            
            return Response({
                'status': 'success',
                'message': f'Permissão removida do grupo {grupo_custom.group.name}'
            })
        except (GrupoCustomizado.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)