from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from accounts.models import Usuario


class TestUsuarioModel(TestCase):
    """Testes para o modelo Usuario"""
    
    def setUp(self):
        """Configuração inicial"""
        self.usuario_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'senha123',
            'first_name': 'Test',
            'last_name': 'User',
            'telefone': '11999999999'
        }
    
    def test_criar_usuario_sucesso(self):
        """Teste: Criar usuário com dados válidos"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        
        self.assertEqual(usuario.username, 'testuser')
        self.assertEqual(usuario.email, 'test@example.com')
        self.assertEqual(usuario.telefone, '11999999999')
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_online)
        self.assertIsNotNone(usuario.last_activity)
        self.assertIsNone(usuario.logout_time)     
    
    def test_criar_superuser_sucesso(self):
        """Teste: Criar superusuário"""
        superuser = Usuario.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
    
    def test_email_unico(self):
        """Teste: Email deve ser único"""
        Usuario.objects.create_user(**self.usuario_data)
        
        with self.assertRaises(Exception):  # IntegrityError
            Usuario.objects.create_user(
                username='outro_user',
                email='test@example.com',  # Email duplicado
                password='senha456'
            )
    
    def test_username_unico(self):
        """Teste: Username deve ser único"""
        Usuario.objects.create_user(**self.usuario_data)
        
        with self.assertRaises(Exception):  # IntegrityError
            Usuario.objects.create_user(
                username='testuser',  # Username duplicado
                email='outro@example.com',
                password='senha456'
            )
    
    def test_str_representation(self):
        """Teste: Representação string do usuário"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        
        # Baseado no resultado real: "Test User (test@example.com)"
        # Mas vimos que retorna " (email)" quando nome está vazio
        expected = 'Test User (test@example.com)'
        self.assertEqual(str(usuario), expected)
    
    def test_marcar_online(self):
        """Teste: Marcar usuário como online"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        
        # Usar método real que existe
        usuario.set_online()
        
        self.assertTrue(usuario.is_online)
        self.assertIsNotNone(usuario.last_activity)
    
    def test_marcar_offline(self):
        """Teste: Marcar usuário como offline"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        
        # Marcar como online primeiro
        usuario.set_online()
        self.assertTrue(usuario.is_online)
        
        # Depois marcar como offline
        usuario.set_offline()
        
        self.assertFalse(usuario.is_online)
        self.assertIsNotNone(usuario.logout_time)
    
    def test_validacao_telefone_formato(self):
        """Teste: Validação de formato do telefone"""
        # Telefone válido
        usuario_data = self.usuario_data.copy()
        usuario_data['telefone'] = '11987654321'
        
        usuario = Usuario(**usuario_data)
        
        try:
            usuario.full_clean()
        except ValidationError:
            self.fail("Telefone válido não deveria dar erro")
    
    def test_grupos_relacionamento(self):
        """Teste: Relacionamento com grupos"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        grupo = Group.objects.create(name='Test Group')
        
        usuario.groups.add(grupo)
        
        self.assertIn(grupo, usuario.groups.all())
        self.assertIn(usuario, grupo.user_set.all())
    
    def test_usuario_inativo_nao_pode_fazer_login(self):
        """Teste: Usuário inativo não consegue fazer login"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        usuario.is_active = False
        usuario.save()
        
        from django.contrib.auth import authenticate
        
        authenticated_user = authenticate(
            username='test@example.com',
            password='senha123'
        )
        
        self.assertIsNone(authenticated_user)
    
    def test_campos_especiais_do_modelo(self):
        """Teste: Campos específicos do modelo Usuario"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        
        # Testar campos que existem
        self.assertIsNotNone(usuario.created_at)
        self.assertIsNotNone(usuario.updated_at)
        self.assertIsNotNone(usuario.last_activity)
        
        # Testar método tempo_offline
        usuario.set_online()
        usuario.set_offline()
        
        # tempo_offline deve ser calculado
        self.assertIsNotNone(usuario.tempo_offline)