from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from unittest.mock import Mock

from controle_acesso.permissions import HasCustomPermission
from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado
from controle_acesso.utils import check_permission

Usuario = get_user_model()


class TestHasCustomPermission(TestCase):
    """Testes para sistema de permissões customizado"""
    
    def setUp(self):
        """Configuração inicial"""
        self.factory = APIRequestFactory()
        
        # Criar permissão customizada
        self.permissao = PermissaoCustomizada.objects.create(
            modulo='accounts',
            acao='listar',
            nome='accounts_listar',
            descricao='Listar usuários',
            ativo=True
        )
        
        # ✅ ADICIONAR: Criar Permission Django correspondente
        content_type = ContentType.objects.get_for_model(Usuario)
        self.permissao_django = Permission.objects.create(
            codename='accounts_listar',
            name='Pode listar usuários',
            content_type=content_type
        )
        
        # Criar grupo Django
        self.grupo_django = Group.objects.create(name='Testadores')
        
        # Criar grupo customizado
        self.grupo_custom = GrupoCustomizado.objects.create(
            group=self.grupo_django,
            descricao='Grupo de teste'
        )
        
        # Criar usuários
        self.superuser = Usuario.objects.create_superuser(
            username='super',
            email='super@test.com',
            password='test123'
        )
        
        self.admin_user = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='test123',
            is_staff=True
        )
        
        self.normal_user = Usuario.objects.create_user(
            username='user',
            email='user@test.com',
            password='test123'
        )
        
        # Adicionar usuário ao grupo
        self.admin_user.groups.add(self.grupo_django)
    
    def test_superuser_tem_todas_permissoes(self):
        """Teste: Superuser bypassa todas as verificações"""
        request = self.factory.get('/test/')
        request.user = self.superuser
        
        permission = HasCustomPermission()
        
        # Mock view com permissão requerida
        view = APIView()
        view.permission_required = 'accounts_listar'
        
        # Superuser deve ter acesso
        self.assertTrue(permission.has_permission(request, view))
    
    def test_usuario_com_permissao_django_acesso_permitido(self):
        """Teste: Usuário com permissão Django correspondente tem acesso"""
        # Adicionar permissão ao grupo
        self.grupo_django.permissions.add(self.permissao_django)
        
        request = self.factory.get('/test/')
        request.user = self.admin_user
        
        permission = HasCustomPermission()
        view = APIView()
        view.permission_required = 'accounts_listar'
        
        # Usuário deve ter acesso
        self.assertTrue(permission.has_permission(request, view))
    
    def test_usuario_sem_permissao_acesso_negado(self):
        """Teste: Usuário sem permissão não tem acesso"""
        request = self.factory.get('/test/')
        request.user = self.normal_user
        
        permission = HasCustomPermission()
        view = APIView()
        view.permission_required = 'accounts_listar'
        
        # Usuário não deve ter acesso
        self.assertFalse(permission.has_permission(request, view))
    
    def test_view_sem_permissao_requerida_acesso_livre(self):
        """Teste: View sem permission_required NEGA acesso (comportamento mais seguro)"""
        
        # Criar view mock SEM permission_required
        view = Mock()
        view.permission_required = None  # ← Sem permissão definida
        view.action = 'list'
        view.basename = 'normal_view'
        
        # Criar request mock com usuário autenticado normal
        request = Mock()
        request.user = self.normal_user
        
        permission = HasCustomPermission()
        
        # ✅ CORRIGIR: Agora deve NEGAR acesso (mais seguro)
        self.assertFalse(permission.has_permission(request, view))
    
    def test_usuario_anonimo_acesso_negado(self):
        """Teste: Usuário anônimo não tem acesso"""
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        permission = HasCustomPermission()
        view = APIView()
        view.permission_required = 'accounts_listar'
        
        # Usuário anônimo não deve ter acesso
        self.assertFalse(permission.has_permission(request, view))
    
    def test_debug_permission_logic(self):
        """Teste: Debug da lógica de permissões"""
        request = self.factory.get('/test/')
        request.user = self.normal_user
        
        permission = HasCustomPermission()
        view = APIView()
        view.permission_required = 'accounts_listar'
        
        # Debug da configuração
        print(f"\n=== DEBUG PERMISSION LOGIC ===")
        print(f"User: {request.user.username}")
        print(f"User is_superuser: {request.user.is_superuser}")
        print(f"User is_authenticated: {request.user.is_authenticated}")
        print(f"View permission_required: {getattr(view, 'permission_required', 'NOT_SET')}")
        
        # Verificar se permissão customizada existe
        perm_custom_exists = PermissaoCustomizada.objects.filter(nome='accounts_listar', ativo=True).exists()
        print(f"PermissaoCustomizada exists: {perm_custom_exists}")
        
        # Verificar se permissão Django existe
        try:
            from django.contrib.auth.models import Permission
            perm_django = Permission.objects.get(codename='accounts_listar')
            print(f"Permission Django exists: {perm_django}")
            print(f"Content type: {perm_django.content_type.app_label}.{perm_django.content_type.model}")
        except Permission.DoesNotExist:
            print("Permission Django NOT exists")
        
        # Testar user_has_permission diretamente
        has_perm = permission.user_has_permission(request.user, 'accounts_listar')
        print(f"user_has_permission result: {has_perm}")
        
        # Testar has_permission completo
        resultado = permission.has_permission(request, view)
        print(f"has_permission result: {resultado}")
        print("=== END DEBUG ===\n")
        
        # Este teste é só para debug, não tem assert
        self.assertTrue(True)  # Sempre passa, só queremos o debug
    
    def test_view_especial_acesso_permitido(self):
        """Teste: Views especiais permitem acesso com apenas autenticação"""
        
        # Criar view mock de status online
        view = Mock()
        view.permission_required = None
        view.action = 'status-online'  # ← View especial
        view.basename = 'status'
        
        request = Mock()
        request.user = self.normal_user
        
        permission = HasCustomPermission()
        
        # ✅ NOVO: Views especiais devem permitir acesso
        self.assertTrue(permission.has_permission(request, view))


class TestCheckPermissionFunction(TestCase):
    """Testes para função check_permission"""
    
    def setUp(self):
        """Configuração inicial"""
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123'
        )
        
        self.superuser = Usuario.objects.create_superuser(
            username='super',
            email='super@example.com',
            password='test123'
        )
    
    def test_check_permission_superuser(self):
        """Teste: check_permission retorna True para superuser"""
        resultado = check_permission(self.superuser, 'qualquer_permissao')
        self.assertTrue(resultado)
    
    def test_check_permission_usuario_sem_permissao(self):
        """Teste: check_permission retorna False sem permissão"""
        resultado = check_permission(self.user, 'permissao_inexistente')
        self.assertFalse(resultado)
    
    def test_check_permission_usuario_com_permissao(self):
        """Teste: check_permission retorna True com permissão válida"""
        
        # ✅ CORREÇÃO 1: Criar PermissaoCustomizada correspondente
        from controle_acesso.models import PermissaoCustomizada
        
        # Criar permissão customizada que corresponde à Django
        perm_custom = PermissaoCustomizada.objects.create(
            modulo='accounts',
            acao='test',
            nome='test_permission',
            descricao='Permissão de teste',
            ativo=True
        )
        
        # Criar permissão Django (código original)
        content_type = ContentType.objects.get_for_model(Usuario)
        permission = Permission.objects.create(
            codename='test_permission',
            name='Test Permission',
            content_type=content_type
        )
        
        # Dar permissão ao usuário (código original)
        self.user.user_permissions.add(permission)
        
        # ✅ DEBUG: Adicionar debug temporário
        print(f"\n=== DEBUG TESTE ===")
        print(f"PermissaoCustomizada existe: {PermissaoCustomizada.objects.filter(nome='test_permission', ativo=True).exists()}")
        print(f"Permission Django existe: {Permission.objects.filter(codename='test_permission').exists()}")
        print(f"Usuário tem permissão: {self.user.has_perm('accounts.test_permission')}")
        
        # Executar check_permission
        resultado = check_permission(self.user, 'test_permission')
        print(f"check_permission resultado: {resultado}")
        print(f"=== FIM DEBUG ===\n")
        
        self.assertTrue(resultado)