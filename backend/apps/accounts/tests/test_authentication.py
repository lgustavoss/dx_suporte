import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Usuario


class TestAutenticacao(TestCase):
    """Testes para sistema de autenticação JWT"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='senha123'
        )
        
        self.login_url = '/api/v1/auth/login/'
        self.refresh_url = '/api/v1/auth/refresh/'
        self.logout_url = '/api/v1/auth/logout/'
    
    def test_login_sucesso_com_email(self):
        """Teste: Login com email e senha válidos"""
        data = {
            'email': 'test@example.com',
            'password': 'senha123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verificar se usuário ficou online
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_online)
        self.assertIsNotNone(self.usuario.last_activity)  # ✅ Campo que existe
    
    def test_login_credenciais_invalidas(self):
        """Teste: Login com credenciais inválidas"""
        data = {
            'email': 'test@example.com',
            'password': 'senha_errada'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_email_inexistente(self):
        """Teste: Login com email inexistente"""
        data = {
            'email': 'inexistente@example.com',
            'password': 'senha123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_usuario_inativo(self):
        """Teste: Login com usuário inativo"""
        self.usuario.is_active = False
        self.usuario.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'senha123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token_sucesso(self):
        """Teste: Renovação de token com refresh token válido"""
        # Fazer login primeiro
        login_data = {
            'email': 'test@example.com',
            'password': 'senha123'
        }
        login_response = self.client.post(self.login_url, login_data)
        
        # Usar refresh token
        refresh_token = login_response.data['refresh']
        refresh_data = {'refresh': refresh_token}
        
        response = self.client.post(self.refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_token_invalido(self):
        """Teste: Renovação com refresh token inválido"""
        refresh_data = {'refresh': 'token_invalido'}
        
        response = self.client.post(self.refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_sucesso(self):
        """Teste: Logout marca usuário como offline"""
        # Fazer login primeiro
        login_data = {
            'email': 'test@example.com',
            'password': 'senha123'
        }
        login_response = self.client.post(self.login_url, login_data)
        
        # Autenticar com token de acesso
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Fazer logout
        refresh_token = login_response.data['refresh']
        logout_data = {'refresh_token': refresh_token}
        
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se usuário ficou offline
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_online)
        self.assertIsNotNone(self.usuario.logout_time)  # ✅ Campo existe
    
    def test_logout_sem_autenticacao(self):
        """Teste: Logout sem estar autenticado"""
        logout_data = {'refresh_token': 'token_qualquer'}
        
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_acesso_endpoint_protegido_sem_token(self):
        """Teste: Acesso a endpoint protegido sem token"""
        response = self.client.get('/api/v1/auth/usuarios/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_acesso_endpoint_protegido_com_token_valido(self):
        """Teste: Acesso a endpoint protegido com token válido"""
        # Fazer login
        login_data = {
            'email': 'test@example.com',
            'password': 'senha123'
        }
        login_response = self.client.post(self.login_url, login_data)
        
        # Autenticar
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Acessar endpoint protegido (pode dar 403 por falta de permissão, mas não 401)
        response = self.client.get('/api/v1/auth/usuarios/')
        
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)