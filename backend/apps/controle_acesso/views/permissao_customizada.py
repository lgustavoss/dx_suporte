from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.controle_acesso.models import PermissaoCustomizada
from ..serializers import PermissaoCustomizadaSerializer
from ..permissions import HasCustomPermission

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
    permission_classes = [HasCustomPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao', 'modulo', 'acao']
    filterset_fields = ['modulo', 'acao', 'ativo']
    ordering_fields = ['nome', 'modulo', 'created_at']
    ordering = ['nome']
    def get_permissions(self):
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
            self.permission_required = 'controle_acesso_gerenciar'
        return [HasCustomPermission()]
