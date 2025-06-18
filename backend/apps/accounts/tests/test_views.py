from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Usuario
from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado


class TestUsuarioViewSet(TestCase):
    """Testes para UsuarioViewSet"""
    
    def setUp(self):
        """Configuração inicial para testes de views"""
        self.client = APIClient()
        
        # Limpar TODAS as permissões de accounts para evitar conflitos
        from controle_acesso.models import PermissaoCustomizada
        PermissaoCustomizada.objects.filter(modulo='accounts').delete()
        
        # Agora criar novas sem conflito
        self.perm_criar = PermissaoCustomizada.objects.create(
            modulo='accounts',
            acao='create_test',  # ← Ação única para testes
            nome='accounts_create_test',
            descricao='Criar usuários (teste)',
            ativo=True,
            auto_descoberta=False
        )
        
        self.perm_listar = PermissaoCustomizada.objects.create(
            modulo='accounts', 
            acao='list_test',  # Ação única para testes
            nome='accounts_list_test',
            descricao='Listar usuários (teste)',
            ativo=True,
            auto_descoberta=False
        )
        
        self.perm_editar = PermissaoCustomizada.objects.create(
            modulo='accounts',
            acao='update_test',  # Ação única para testes
            nome='accounts_update_test',
            descricao='Editar usuários (teste)',
            ativo=True,
            auto_descoberta=False
        )
        
        self.perm_excluir = PermissaoCustomizada.objects.create(
            modulo='accounts',
            acao='delete_test',  # Ação única para testes
            nome='accounts_delete_test',
            descricao='Excluir usuários (teste)',
            ativo=True,
            auto_descoberta=False
        )
        
        # Criar usuários de teste únicos
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        
        # Limpar usuários de teste existentes
        Usuario.objects.filter(username__startswith='test_').delete()
        
        self.admin_user = Usuario.objects.create_user(
            username='test_admin_views',
            email='test_admin_views@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.normal_user = Usuario.objects.create_user(
            username='test_user_views',
            email='test_user_views@example.com', 
            password='testpass123'
        )
        
        # Criar grupos únicos
        from django.contrib.auth.models import Group
        self.admin_group, _ = Group.objects.get_or_create(name='Test Admin Group Views')
        self.user_group, _ = Group.objects.get_or_create(name='Test User Group Views')
        
        # Associar usuários aos grupos
        self.admin_user.groups.add(self.admin_group)
        self.normal_user.groups.add(self.user_group)
        
        # Adicionar permissões ao grupo admin
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission
        
        # Adicionar todas as permissões ao admin
        self.admin_group.permissions.add(
            Permission.objects.get_or_create(
                codename='add_usuario',
                content_type=ContentType.objects.get_for_model(Usuario)
            )[0]
        )
        
        # URLs
        self.usuarios_url = '/api/v1/auth/usuarios/'
        self.login_url = '/api/v1/auth/login/'
    
    def test_listar_usuarios_com_permissao(self):
        """Teste: Listar usuários com permissão adequada"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.usuarios_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_listar_usuarios_sem_permissao(self):
        """Teste: Listar usuários sem permissão"""
        self.client.force_authenticate(user=self.normal_user)  # Usuário sem grupo/permissões
        
        response = self.client.get(self.usuarios_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_listar_usuarios_sem_autenticacao(self):
        """Teste: Listar usuários sem estar autenticado"""
        response = self.client.get(self.usuarios_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_criar_usuario_com_permissao(self):
        """Teste: Criar usuário com permissão adequada"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',  # ✅ ADICIONAR confirmação
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.usuarios_url, data)
        
        # DEBUG: Ver o erro se ainda falhar
        if response.status_code != 201:
            print(f"DEBUG: Status: {response.status_code}, Data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(username='newuser').exists())
    
    def test_criar_usuario_sem_permissao(self):
        """Teste: Criar usuário sem permissão"""
        self.client.force_authenticate(user=self.normal_user)  # Só tem permissão de visualizar
        
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpass123'
        }
        
        response = self.client.post(self.usuarios_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_editar_usuario_com_permissao(self):
        """Teste: Editar usuário com permissão adequada"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {'first_name': 'Nome Atualizado'}
        url = f'{self.usuarios_url}{self.normal_user.id}/'
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Nome Atualizado')
    
    def test_editar_usuario_autoexclusao_bloqueada(self):
        """Teste: Validação de autodesativação bloqueada"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {'is_active': False}
        url = f'{self.usuarios_url}{self.admin_user.id}/'
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('não pode desativar', str(response.data))
    
    def test_excluir_usuario_com_permissao(self):
        """Teste: Excluir usuário com permissão adequada"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'{self.usuarios_url}{self.normal_user.id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar soft delete
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.is_active)
    
    def test_excluir_usuario_autoexclusao_bloqueada(self):
        """Teste: Autoexclusão bloqueada"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'{self.usuarios_url}{self.admin_user.id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('não pode excluir sua própria conta', str(response.data))
    
    def test_busca_global_usuarios(self):
        """Teste: Busca global por palavra-chave"""
        self.client.force_authenticate(user=self.admin_user)
        
        # ✅ CORRIGIDO: Buscar por nome que existe
        response = self.client.get(f'{self.usuarios_url}?search=test_admin_views')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve encontrar o usuário admin
        usernames = [user['username'] for user in response.data['results']]
        self.assertIn('test_admin_views', usernames)  # ← Nome correto
    
    def test_paginacao_usuarios(self):
        """Teste: Paginação funcionando"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'{self.usuarios_url}?page_size=1&page=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)
    
    def test_filtro_usuarios_online(self):
        """Teste: Filtro de usuários online"""
        self.client.force_authenticate(user=self.admin_user)
        
        # ✅ CORRIGIDO: Usar método real
        self.normal_user.set_online()  # ← Método correto
        
        response = self.client.get(f'{self.usuarios_url}?is_online=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se retornou apenas usuários online
        for user_data in response.data['results']:
            user = Usuario.objects.get(id=user_data['id'])
            self.assertTrue(user.is_online)


class TestViewsExtras(TestCase):
    """Testes para endpoints extras"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = APIClient()
        
        # ✅ CORRIGIDO: Usar nomes consistentes
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        
        self.admin_user = Usuario.objects.create_user(
            username='test_admin_views',  # ← Nome consistente
            email='test_admin_views@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.normal_user = Usuario.objects.create_user(
            username='test_user_views',  # ← Nome consistente
            email='test_user_views@example.com', 
            password='testpass123'
        )

    def test_status_online_endpoint(self):
        """Teste: Endpoint de status online"""
        # ✅ CORRIGIDO: Usar force_authenticate
        self.client.force_authenticate(user=self.normal_user)
        
        response = self.client.get('/api/v1/auth/status-online/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('usuarios_online', response.data)

    def test_minhas_permissoes_endpoint(self):
        """Teste: Endpoint de minhas permissões"""
        # Autenticar usuário normal
        self.client.force_authenticate(user=self.normal_user)
        
        response = self.client.get('/api/v1/auth/minhas-permissoes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estrutura da resposta
        self.assertIn('usuario', response.data)
        self.assertIn('permissoes', response.data)  
        self.assertIn('total', response.data)
        self.assertIn('is_superuser', response.data)
        
        # ✅ CORRIGIDO: Nome correto
        self.assertEqual(response.data['usuario'], 'test_user_views')
        self.assertFalse(response.data['is_superuser'])
        self.assertIsInstance(response.data['permissoes'], list)
        self.assertIsInstance(response.data['total'], int)