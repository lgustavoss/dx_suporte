from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import Group, Permission
from django_filters.rest_framework import DjangoFilterBackend

from .models import GrupoCustomizado, PermissaoCustomizada
from .serializers import (
    GrupoCustomizadoSerializer, 
    PermissaoCustomizadaSerializer,
    UsuarioSimplificadoSerializer,
    GrupoSimplificadoSerializer,
)
from accounts.models import Usuario
from .permissions import RequirePermission, HasCustomPermission
from core.filters import GlobalSearchFilter, GrupoFilter
from core.pagination import CustomPagination

@RequirePermission('controle_acesso_visualizar')
class GrupoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar grupos com paginação e filtros"""
    queryset = GrupoCustomizado.objects.all().order_by('group__name')  # ← CORREÇÃO AQUI
    serializer_class = GrupoCustomizadoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, GlobalSearchFilter, filters.OrderingFilter]
    filterset_class = GrupoFilter
    
    # Campos de busca global (corrigidos para campos reais)
    search_fields = [
        'group__name',   # ← CORREÇÃO: Busca no nome do grupo via FK
        'descricao',     # Busca na descrição
    ]
    
    # Campos disponíveis para ordenação (corrigidos)
    ordering_fields = ['group__name', 'created_at', 'updated_at', 'ativo']  # ← CORREÇÃO
    ordering = ['group__name']  # ← CORREÇÃO: Ordenação padrão
    
    def get_permissions(self):
        """Definir permissões baseadas na action"""
        if self.action == 'list':
            self.required_permission = 'controle_acesso_visualizar'
        elif self.action == 'retrieve':
            self.required_permission = 'controle_acesso_visualizar'
        elif self.action == 'create':
            self.required_permission = 'controle_acesso_criar'
        elif self.action in ['update', 'partial_update']:
            self.required_permission = 'controle_acesso_editar'
        elif self.action == 'destroy':
            self.required_permission = 'controle_acesso_excluir'
        
        return super().get_permissions()
    
    def get_queryset(self):
        """Query customizada para incluir grupos inativos se necessário"""
        queryset = GrupoCustomizado.objects.all().order_by('group__name')  # ← CORREÇÃO
        
        # Filtrar grupos inativos por padrão
        include_inactive = self.request.query_params.get('include_inactive', 'false')
        if include_inactive.lower() != 'true':
            queryset = queryset.filter(ativo=True)
        
        return queryset

@RequirePermission('controle_acesso_visualizar')
class PermissaoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para listar permissões com busca"""
    queryset = PermissaoCustomizada.objects.all().order_by('modulo', 'nome')  # ← OK, estes são campos reais
    serializer_class = PermissaoCustomizadaSerializer
    pagination_class = CustomPagination
    filter_backends = [GlobalSearchFilter, filters.OrderingFilter]
    
    # Campos de busca global
    search_fields = [
        'nome',         # Busca no nome da permissão
        'descricao',    # Busca na descrição
        'modulo',       # Busca no módulo
    ]
    
    ordering_fields = ['nome', 'modulo', 'created_at']
    ordering = ['modulo', 'nome']

@RequirePermission('controle_acesso_editar')
class GrupoUsuariosView(APIView):
    """Gerenciar usuários em grupos"""
    def get(self, request, grupo_id):
        # GET requer apenas visualizar
        self.required_permission = 'controle_acesso_visualizar'
        
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuarios = grupo_custom.group.user_set.filter(is_active=True)
            serializer = UsuarioSimplificadoSerializer(usuarios, many=True)
            
            usuarios_data = [u for u in serializer.data if u is not None]
            
            return Response({
                'grupo': grupo_custom.nome,  # ← Esta propriedade funciona aqui
                'usuarios': usuarios_data,
                'total': len(usuarios_data)
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, grupo_id):
        """Adicionar usuários ao grupo"""
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuarios_ids = request.data.get('usuarios_ids', [])
            added_count = 0
            
            for user_id in usuarios_ids:
                try:
                    usuario = Usuario.objects.get(id=user_id, is_active=True)
                    grupo_custom.group.user_set.add(usuario)
                    added_count += 1
                except Usuario.DoesNotExist:
                    continue
            
            return Response({
                'message': f'{added_count} usuários adicionados ao grupo {grupo_custom.nome}',
                'success': True
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@RequirePermission('controle_acesso_editar')
class RemoverUsuarioGrupoView(APIView):
    """Remover usuário de um grupo"""
    def delete(self, request, grupo_id, usuario_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            usuario = Usuario.objects.get(id=usuario_id)
            grupo_custom.group.user_set.remove(usuario)
            
            return Response({
                'message': f'Usuário {usuario.username} removido do grupo {grupo_custom.nome}',
                'success': True
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@RequirePermission('controle_acesso_editar')
class GrupoPermissoesView(APIView):
    """Gerenciar permissões em grupos"""
    def get(self, request, grupo_id):
        # GET requer apenas visualizar
        self.required_permission = 'controle_acesso_visualizar'
        
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permissoes_django = grupo_custom.group.permissions.all()
            
            # Converter para nossas permissões customizadas
            permissoes_custom = []
            for perm_django in permissoes_django:
                try:
                    perm_custom = PermissaoCustomizada.objects.get(nome=perm_django.codename)
                    permissoes_custom.append(perm_custom)
                except PermissaoCustomizada.DoesNotExist:
                    continue
            
            serializer = PermissaoCustomizadaSerializer(permissoes_custom, many=True)
            return Response({
                'grupo': grupo_custom.nome,
                'permissoes': serializer.data,
                'total': len(permissoes_custom)
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, grupo_id):
        """Adicionar permissões ao grupo"""
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            permissoes_ids = request.data.get('permissoes_ids', [])
            added_count = 0

            for perm_id in permissoes_ids:
                try:
                    perm_custom = PermissaoCustomizada.objects.get(id=perm_id)
                    # Buscar a permissão do Django correspondente
                    perm_django = Permission.objects.get(codename=perm_custom.nome)
                    grupo_custom.group.permissions.add(perm_django)
                    added_count += 1
                except (PermissaoCustomizada.DoesNotExist, Permission.DoesNotExist):
                    continue

            return Response({
                'message': f'{added_count} permissões adicionadas ao grupo {grupo_custom.nome}',
                'success': True
            })
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@RequirePermission('controle_acesso_editar')
class RemoverPermissaoGrupoView(APIView):
    """Remover permissão de um grupo"""
    def delete(self, request, grupo_id, permissao_id):
        try:
            grupo_custom = GrupoCustomizado.objects.get(id=grupo_id)
            perm_custom = PermissaoCustomizada.objects.get(id=permissao_id)
            
            # Buscar a permissão do Django correspondente
            try:
                perm_django = Permission.objects.get(codename=perm_custom.nome)
                grupo_custom.group.permissions.remove(perm_django)
                
                return Response({
                    'message': f'Permissão {perm_custom.nome} removida do grupo {grupo_custom.nome}',
                    'success': True
                })
            except Permission.DoesNotExist:
                return Response({'error': 'Permissão não encontrada no grupo'}, status=status.HTTP_404_NOT_FOUND)
                
        except GrupoCustomizado.DoesNotExist:
            return Response({'error': 'Grupo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except PermissaoCustomizada.DoesNotExist:
            return Response({'error': 'Permissão não encontrada'}, status=status.HTTP_404_NOT_FOUND)

class SyncPermissoesView(APIView):
    """Sincronizar permissões automaticamente"""
    permission_classes = [HasCustomPermission]
    required_permission = 'controle_acesso_criar'
    
    def post(self, request):
        from .utils import sync_permissions
        try:
            created_count = sync_permissions()
            return Response({
                "message": f"{created_count} novas permissões criadas!",
                "success": True
            })
        except Exception as e:
            return Response({
                "message": f"Erro ao sincronizar: {str(e)}",
                "success": False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)