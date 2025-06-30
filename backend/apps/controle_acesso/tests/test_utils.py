from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado
from controle_acesso.utils import check_permission

Usuario = get_user_model()


class TestCheckPermissionFunction(TestCase):
    """Testes para função check_permission em utils.py"""
    
    def setUp(self):
        """Configuração inicial"""
        # Criar usuários
        self.superuser = Usuario.objects.create_superuser(
            username='super',
            email='super@test.com',
            password='test123'
        )
        
        self.normal_user = Usuario.objects.create_user(
            username='user',
            email='user@test.com',
            password='test123'
        )
        
        # Criar permissão customizada ativa
        self.permissao_ativa = PermissaoCustomizada.objects.create(
            modulo='test',
            acao='criar',
            nome='test_criar',
            descricao='Criar items de teste',
            ativo=True
        )
        
        # Criar permissão customizada inativa
        self.permissao_inativa = PermissaoCustomizada.objects.create(
            modulo='test',
            acao='excluir',
            nome='test_excluir',
            descricao='Excluir items de teste',
            ativo=False
        )
    
    def test_check_permission_superuser_bypass(self):
        """Teste: Superuser sempre retorna True"""
        resultado = check_permission(self.superuser, 'qualquer_permissao')
        self.assertTrue(resultado)
    
    def test_check_permission_usuario_sem_permissao(self):
        """Teste: Usuário normal sem permissão retorna False"""
        resultado = check_permission(self.normal_user, 'test_criar')
        self.assertFalse(resultado)
    
    def test_check_permission_usuario_com_permissao_django_ativa(self):
        """Teste: Usuário com permissão Django + customizada ativa"""
        # Criar permissão Django correspondente
        content_type = ContentType.objects.get_for_model(Usuario)
        perm_django = Permission.objects.create(
            codename='test_criar',
            name='Pode criar teste',
            content_type=content_type
        )
        
        # Dar permissão ao usuário
        self.normal_user.user_permissions.add(perm_django)
        
        # Deve retornar True
        resultado = check_permission(self.normal_user, 'test_criar')
        self.assertTrue(resultado)
    
    def test_check_permission_permissao_inexistente(self):
        """Teste: Permissão inexistente retorna False"""
        resultado = check_permission(self.normal_user, 'permissao_inexistente')
        self.assertFalse(resultado)
    
    def test_check_permission_usuario_via_grupo(self):
        """Teste: Usuário com permissão via grupo"""
        # Criar grupo
        grupo = Group.objects.create(name='Testadores')
        
        # Criar permissão Django
        content_type = ContentType.objects.get_for_model(Usuario)
        perm_django = Permission.objects.create(
            codename='test_via_grupo',
            name='Teste via grupo',
            content_type=content_type
        )
        
        # Criar permissão customizada
        PermissaoCustomizada.objects.create(
            modulo='test',
            acao='grupo',
            nome='test_via_grupo',
            descricao='Teste via grupo',
            ativo=True
        )
        
        # Adicionar permissão ao grupo
        grupo.permissions.add(perm_django)
        
        # Adicionar usuário ao grupo
        self.normal_user.groups.add(grupo)
        
        # Deve retornar True
        resultado = check_permission(self.normal_user, 'test_via_grupo')
        self.assertTrue(resultado)