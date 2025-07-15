from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone

from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioBasicoSerializer,
    UsuarioDetalhadoSerializer,
    UsuarioCreateSerializer,
    CustomTokenObtainPairSerializer
)
from apps.controle_acesso.models import GrupoCustomizado
from controle_acesso.serializers import GrupoSimplificadoSerializer
from controle_acesso.permissions import RequirePermission, HasCustomPermission
from core.filters import GlobalSearchFilter, UsuarioFilter
from core.pagination import CustomPagination
from .validators import ValidacaoCompleta 

@extend_schema(
    summary="Login JWT",
    description="Autentica usuário e retorna tokens JWT (access + refresh)",
    tags=['Autenticação'], 
    request=CustomTokenObtainPairSerializer,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access': {'type': 'string'},
                'refresh': {'type': 'string'},
                'user': {'type': 'object'}
            }
        }
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Login customizado que marca usuário como online"""
    serializer_class = CustomTokenObtainPairSerializer

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

@extend_schema(
    summary="Logout",
    description="Desloga usuário e adiciona refresh token à blacklist",
    tags=['Autenticação'],  
    request={
        'type': 'object',
        'properties': {
            'refresh_token': {'type': 'string'}
        }
    },
    responses={200: {'description': 'Logout realizado com sucesso'}}
)
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

@extend_schema(
    summary="Status Online",
    description="Lista usuários atualmente online no sistema",
    tags=['Utilitários'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'usuarios_online': {'type': 'array'},
                'total': {'type': 'integer'},
                'timestamp': {'type': 'string'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status_online(request):
    """Endpoint para verificar usuários online"""
    usuarios_online = Usuario.objects.filter(
        last_activity__gte=timezone.now() - timezone.timedelta(minutes=15)
    ).values('id', 'username', 'first_name', 'last_name')
    
    return Response({
        'usuarios_online': list(usuarios_online),
        'total': usuarios_online.count(),
        'timestamp': timezone.now().isoformat()
    })

@extend_schema_view(
    list=extend_schema(
        summary="Listar usuários",
        description="Lista usuários com paginação e filtros",
        tags=['Usuários'],  
    ),
    create=extend_schema(
        summary="Criar usuário", 
        description="Cria novo usuário no sistema",
        tags=['Usuários'],  
    ),
    retrieve=extend_schema(
        summary="Detalhes do usuário",
        description="Obtém detalhes de um usuário específico",
        tags=['Usuários'],  
    ),
    update=extend_schema(
        summary="Atualizar usuário",
        description="Atualiza dados do usuário",
        tags=['Usuários'],  
    ),
    partial_update=extend_schema(
        summary="Atualizar usuário parcialmente",
        description="Atualiza dados específicos do usuário (PATCH)",
        tags=['Usuários'],
    ),
    destroy=extend_schema(
        summary="Excluir usuário",
        description="Remove usuário do sistema",
        tags=['Usuários'],  
    ),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gerenciar usuários com validações de segurança"""
    queryset = Usuario.objects.filter(is_active=True).order_by('username')
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, GlobalSearchFilter, filters.OrderingFilter]
    filterset_class = UsuarioFilter
    
    # Campos de busca global
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'telefone',
    ]
    
    ordering_fields = [
        'username', 'email', 'first_name', 'last_name', 
        'date_joined', 'last_login', 'is_online'
    ]
    ordering = ['username']
    
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
        
        include_inactive = self.request.query_params.get('include_inactive', 'false')
        if include_inactive.lower() != 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Exclusão com validações de segurança"""
        instance = self.get_object()
        
        # ✅ APLICAR VALIDAÇÕES DE EXCLUSÃO
        try:
            ValidacaoCompleta.validar_exclusao_usuario(request.user, instance)
        except serializers.ValidationError as e:
            return Response(
                e.detail, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Se passou nas validações, executar exclusão
        self.perform_destroy(instance)
        return Response(
            {"detail": "✅ Usuário excluído com sucesso."}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
    def perform_destroy(self, instance):
        """Soft delete ao invés de exclusão definitiva"""
        instance.is_active = False
        instance.save()

@extend_schema(
    summary="Grupos do Usuário",
    description="Lista e gerencia grupos de um usuário específico",
    tags=['Usuários'],
    responses={200: {'description': 'Lista de grupos do usuário'}}
)
@RequirePermission('accounts_visualizar')
class UsuarioGruposView(APIView):
    """Listar grupos de um usuário específico (perspectiva do usuário)"""
    permission_classes = [IsAuthenticated, HasCustomPermission]
    
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

@extend_schema(
    summary="Status Online Pessoal",
    description="Verifica e atualiza status online do usuário autenticado",
    tags=['Utilitários'],  
    responses={
        200: {
            'type': 'object',
            'properties': {
                'user': {'type': 'string'},
                'is_online': {'type': 'boolean'},
                'last_activity': {'type': 'string'},
                'session_duration': {'type': 'string'}
            }
        }
    }
)
class StatusOnlineView(APIView):
    """Endpoint para verificar e atualizar o status online do usuário autenticado"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retorna o status online do usuário"""
        usuario = request.user
        is_online = usuario.is_online
        last_activity = usuario.last_activity.isoformat() if usuario.last_activity else None
        
        # Atualiza a última atividade para agora
        usuario.last_activity = timezone.now()
        usuario.save(update_fields=['last_activity'])
        
        return Response({
            "user": usuario.username,
            "is_online": is_online,
            "last_activity": last_activity,
            "session_duration": self.calcular_duracao_sessao(usuario)
        })
    
    def calcular_duracao_sessao(self, usuario):
        """Calcula a duração da sessão do usuário"""
        if usuario.last_login:
            duracao = timezone.now() - usuario.last_login
            return str(duracao).split(".")[0]  # Retorna no formato HH:MM:SS
        return "00:00:00"

@extend_schema(
    summary="Minhas Permissões",
    description="Lista permissões do usuário autenticado",
    tags=['Utilitários'],  
    responses={
        200: {
            'type': 'object',
            'properties': {
                'usuario': {'type': 'string'},
                'permissoes': {'type': 'array'},
                'total': {'type': 'integer'},
                'is_superuser': {'type': 'boolean'}
            }
        }
    }
)
class MinhasPermissoesView(APIView):
    """Endpoint para usuário ver suas próprias permissões"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from controle_acesso.utils import get_user_permissions
        from controle_acesso.serializers import PermissaoCustomizadaSerializer
        
        permissoes = get_user_permissions(request.user)
        serializer = PermissaoCustomizadaSerializer(permissoes, many=True)
        
        return Response({
            'usuario': request.user.username,
            'permissoes': serializer.data,
            'total': len(serializer.data),
            'is_superuser': request.user.is_superuser
        })

@extend_schema(
    summary="Refresh Token",
    description="Renova token de acesso usando refresh token válido",
    tags=['Autenticação'],
    request={
        'type': 'object',
        'properties': {
            'refresh': {'type': 'string', 'description': 'Token de refresh válido'}
        },
        'required': ['refresh']
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access': {'type': 'string', 'description': 'Novo token de acesso'}
            }
        },
        401: {'description': 'Token de refresh inválido ou expirado'}
    }
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    Endpoint para renovar token de acesso usando refresh token
    
    O refresh token é válido por mais tempo que o access token,
    permitindo renovação automática sem novo login.
    """
    pass

@extend_schema(
    summary="Meus Dados",
    description="Retorna dados completos do usuário autenticado",
    tags=['Utilitários'],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'username': {'type': 'string'},
                'email': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'full_name': {'type': 'string'},
                'telefone': {'type': 'string'},
                'is_active': {'type': 'boolean'},
                'is_online': {'type': 'boolean'},
                'date_joined': {'type': 'string'},
                'last_login': {'type': 'string'},
                'last_activity': {'type': 'string'},
                'logout_time': {'type': 'string'},
                'total_grupos': {'type': 'integer'},
                'grupos_nomes': {'type': 'array'}
            }
        }
    }
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Endpoint para dados do usuário autenticado"""
    if request.method == 'GET':
        # Retornar dados completos do usuário
        from .serializers import UsuarioDetalhadoSerializer
        serializer = UsuarioDetalhadoSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Atualizar dados do usuário
        from .serializers import UsuarioSerializer
        
        # Validações de segurança
        ValidacaoSeguranca.validar_autoexclusao(request.user, request.data)
        
        serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Retornar dados atualizados
            response_serializer = UsuarioDetalhadoSerializer(request.user)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)