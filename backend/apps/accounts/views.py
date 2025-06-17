from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioBasicoSerializer,
    UsuarioDetalhadoSerializer,
    UsuarioCreateSerializer,
    CustomTokenObtainPairSerializer
)
from controle_acesso.models import GrupoCustomizado
from controle_acesso.serializers import GrupoSimplificadoSerializer
from controle_acesso.permissions import RequirePermission, HasCustomPermission
from core.filters import GlobalSearchFilter, UsuarioFilter
from core.pagination import CustomPagination

class CustomTokenObtainPairView(TokenObtainPairView):
    """Login customizado que marca usuário como online"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]  # Login deve ser público
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            email = request.data.get('email')
            try:
                user = Usuario.objects.get(email=email)
                user.set_online()
            except Usuario.DoesNotExist:
                pass
        return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout que marca usuário como offline"""
    try:
        request.user.set_offline()
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Logout realizado com sucesso',
            'logout_time': request.user.logout_time
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Erro ao realizar logout'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasCustomPermission])
def status_online_view(request):
    """Endpoint para verificar status online/offline dos usuários"""
    # Definir permissão necessária para esta view
    request.required_permission = 'accounts_visualizar'
    
    usuarios_online = Usuario.objects.filter(is_online=True)
    serializer = UsuarioBasicoSerializer(usuarios_online, many=True)
    
    return Response({
        'usuarios_online': serializer.data,
        'total_online': usuarios_online.count()
    })

@RequirePermission('accounts_visualizar')
class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gerenciar usuários com paginação e filtros"""
    queryset = Usuario.objects.filter(is_active=True).order_by('username')
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, GlobalSearchFilter, filters.OrderingFilter]
    filterset_class = UsuarioFilter
    
    # Campos de busca global (busca em qualquer um desses campos)
    search_fields = [
        'username',      # Busca no nome de usuário
        'email',         # Busca no email
        'first_name',    # Busca no primeiro nome
        'last_name',     # Busca no sobrenome
        'telefone',      # Busca no telefone
    ]
    
    # Campos disponíveis para ordenação
    ordering_fields = [
        'username', 'email', 'first_name', 'last_name', 
        'date_joined', 'last_login', 'is_online'
    ]
    ordering = ['username']  # Ordenação padrão
    
    def get_serializer_class(self):
        """Escolher serializer baseado na action"""
        if self.action == 'list':
            return UsuarioBasicoSerializer
        elif self.action == 'retrieve':
            return UsuarioDetalhadoSerializer
        elif self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioSerializer
        return UsuarioBasicoSerializer
    
    def get_permissions(self):
        """Definir permissões baseadas na action"""
        if self.action == 'list':
            self.required_permission = 'accounts_visualizar'
        elif self.action == 'retrieve':
            self.required_permission = 'accounts_visualizar'
        elif self.action == 'create':
            self.required_permission = 'accounts_criar'
        elif self.action in ['update', 'partial_update']:
            self.required_permission = 'accounts_editar'
        elif self.action == 'destroy':
            self.required_permission = 'accounts_excluir'
        
        return super().get_permissions()
    
    def get_queryset(self):
        """Query customizada para incluir usuários inativos se necessário"""
        queryset = Usuario.objects.all().order_by('username')
        
        # Filtrar usuários inativos por padrão, mas permitir ver todos se solicitado
        include_inactive = self.request.query_params.get('include_inactive', 'false')
        if include_inactive.lower() != 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset

@RequirePermission('accounts_visualizar')
class UsuarioGruposView(APIView):
    """Listar grupos de um usuário específico (perspectiva do usuário)"""
    def get(self, request, usuario_id):
        try:
            usuario = Usuario.objects.get(id=usuario_id, is_active=True)
            grupos_django = usuario.groups.all()
            grupos_custom = GrupoCustomizado.objects.filter(
                group__in=grupos_django, 
                ativo=True
            )
            
            serializer = GrupoSimplificadoSerializer(grupos_custom, many=True)
            grupos_data = [g for g in serializer.data if g is not None]
            
            return Response({
                'usuario': usuario.username,
                'grupos': grupos_data,
                'total': len(grupos_data)
            })
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuário não encontrado ou inativo'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_permissoes_view(request):
    """Endpoint para usuário ver suas próprias permissões"""
    from controle_acesso.permissions import get_user_permissions
    from controle_acesso.serializers import PermissaoCustomizadaSerializer
    
    permissoes = get_user_permissions(request.user)
    serializer = PermissaoCustomizadaSerializer(permissoes, many=True)
    
    return Response({
        'usuario': request.user.username,
        'permissoes': serializer.data,
        'total': len(serializer.data),
        'is_superuser': request.user.is_superuser
    })