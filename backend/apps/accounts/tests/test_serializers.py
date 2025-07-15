from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory
from apps.accounts.models import Usuario
from accounts.serializers import (
    UsuarioBasicoSerializer,
    UsuarioDetalhadoSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer
)


class TestUsuarioSerializers(TestCase):
    """Testes para serializers de usuário"""
    
    def setUp(self):
        """Configuração inicial"""
        self.factory = APIRequestFactory()
        self.grupo = Group.objects.create(name='Test Group')
        
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='senha123',
            first_name='Test',
            last_name='User',
            telefone='11999999999'
        )
        self.usuario.groups.add(self.grupo)
        
        self.admin = Usuario.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    def test_usuario_basico_serializer(self):
        """Teste: UsuarioBasicoSerializer serializa campos básicos"""
        serializer = UsuarioBasicoSerializer(self.usuario)
        
        expected_fields = {'id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_online'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertTrue(serializer.data['is_active'])
    
    def test_usuario_detalhado_serializer(self):
        """Teste: UsuarioDetalhadoSerializer inclui grupos"""
        # Limpar grupos para teste isolado
        self.usuario.groups.clear()
        
        # Adicionar grupo específico do teste
        grupo = Group.objects.create(name='Test Group Detalhado Único')
        self.usuario.groups.add(grupo)
        
        serializer = UsuarioDetalhadoSerializer(self.usuario)
        
        self.assertIn('grupos_nomes', serializer.data)
        self.assertIn('total_grupos', serializer.data)
        self.assertEqual(serializer.data['total_grupos'], 1)
        self.assertIn('Test Group Detalhado Único', serializer.data['grupos_nomes'])

    def test_usuario_create_serializer_dados_validos(self):
        """Teste: UsuarioCreateSerializer cria usuário com dados válidos"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'senha123',
            'password_confirm': 'senha123',  
            'first_name': 'New',
            'last_name': 'User',
            'telefone': '11888888888'
        }
        
        serializer = UsuarioCreateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), f"Erros: {serializer.errors}")
        
        usuario = serializer.save()
        self.assertEqual(usuario.username, 'newuser')
        self.assertEqual(usuario.email, 'newuser@example.com')
        self.assertTrue(usuario.check_password('senha123'))
    
    def test_usuario_create_serializer_email_duplicado(self):
        """Teste: UsuarioCreateSerializer rejeita email duplicado"""
        data = {
            'username': 'newuser',
            'email': 'test@example.com',  # Email já existe
            'password': 'newpassword123'
        }
        
        serializer = UsuarioCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_usuario_create_serializer_username_duplicado(self):
        """Teste: UsuarioCreateSerializer rejeita username duplicado"""
        data = {
            'username': 'testuser',  # Username já existe
            'email': 'new@example.com',
            'password': 'newpassword123'
        }
        
        serializer = UsuarioCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_usuario_create_serializer_senhas_diferentes(self):
        """Teste: UsuarioCreateSerializer rejeita senhas diferentes"""
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'senha123',
            'password_confirm': 'senha456',  # ❌ Senha diferente
            'first_name': 'New',
            'last_name': 'User',
            'telefone': '11777777777'
        }
        
        serializer = UsuarioCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        # O erro vem em password_confirm, não em password
        self.assertIn('password_confirm', serializer.errors)
        self.assertIn('não coincidem', str(serializer.errors['password_confirm'][0]))
    
    def test_usuario_serializer_alterar_senha_com_senha_atual(self):
        """Teste: UsuarioSerializer altera senha com senha atual válida"""
        request = self.factory.patch('/')
        request.user = self.usuario
        
        data = {
            'password': 'nova_senha123',
            'password_atual': 'senha123'
        }
        
        serializer = UsuarioSerializer(
            self.usuario, 
            data=data, 
            partial=True,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
        
        usuario_atualizado = serializer.save()
        
        self.assertTrue(usuario_atualizado.check_password('nova_senha123'))
    
    def test_usuario_serializer_alterar_senha_sem_senha_atual(self):
        """Teste: UsuarioSerializer rejeita alteração de senha sem senha atual"""
        request = self.factory.patch('/')
        request.user = self.usuario
        
        data = {
            'password': 'nova_senha123'
            # Sem password_atual
        }
        
        serializer = UsuarioSerializer(
            self.usuario, 
            data=data, 
            partial=True,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_atual', serializer.errors)
    
    def test_usuario_serializer_senha_atual_incorreta(self):
        """Teste: UsuarioSerializer rejeita senha atual incorreta"""
        request = self.factory.patch('/')
        request.user = self.usuario
        
        data = {
            'password': 'nova_senha123',
            'password_atual': 'senha_errada'
        }
        
        serializer = UsuarioSerializer(
            self.usuario, 
            data=data, 
            partial=True,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_atual', serializer.errors)
    
    def test_usuario_serializer_admin_altera_senha_sem_senha_atual(self):
        """Teste: Admin pode alterar senha de outro usuário sem senha atual"""
        admin_group = Group.objects.create(name='Administradores')
        self.admin.groups.add(admin_group)
        
        request = self.factory.patch('/')
        request.user = self.admin
        
        data = {
            'password': 'nova_senha_admin123'
            # Admin não precisa da senha atual do outro usuário
        }
        
        serializer = UsuarioSerializer(
            self.usuario, 
            data=data, 
            partial=True,
            context={'request': request}
        )
        
        # Deve ser válido mesmo sem password_atual
        self.assertTrue(serializer.is_valid())
    
    def test_usuario_serializer_aplicar_validacoes_seguranca(self):
        """Teste: UsuarioSerializer aplica validações de segurança"""
        request = self.factory.patch('/')
        request.user = self.usuario
        
        # Tentar desativar própria conta
        data = {'is_active': False}
        
        serializer = UsuarioSerializer(
            self.usuario, 
            data=data, 
            partial=True,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        # Deve conter erro de validação de segurança
        self.assertTrue(any('não pode desativar' in str(error) for error in serializer.errors.values()))