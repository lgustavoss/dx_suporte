import pytest
from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework import serializers
from accounts.models import Usuario
from accounts.validators import ValidacaoCompleta, ValidacaoSeguranca


class TestValidacoesSeguranca(TestCase):
    """Testes para validações críticas de segurança"""
    
    def setUp(self):
        """Configuração inicial para todos os testes"""
        # Criar grupos
        self.grupo_admin = Group.objects.create(name='Administradores')
        self.grupo_user = Group.objects.create(name='Usuários')
        
        # Criar usuários de teste
        self.admin1 = Usuario.objects.create_user(
            username='admin1',
            email='admin1@test.com',
            password='teste123'
        )
        self.admin1.groups.add(self.grupo_admin)
        
        self.admin2 = Usuario.objects.create_user(
            username='admin2',
            email='admin2@test.com',
            password='teste123'
        )
        self.admin2.groups.add(self.grupo_admin)
        
        self.user_normal = Usuario.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='teste123'
        )
        self.user_normal.groups.add(self.grupo_user)
        
        # Criar superusuário
        self.superuser = Usuario.objects.create_superuser(
            username='superuser',
            email='super@test.com',
            password='teste123'
        )
    
    def test_nao_autoexclusao_deve_falhar(self):
        """Teste: Usuário não pode excluir própria conta"""
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_nao_autoexclusao(self.admin1, self.admin1)
        
        self.assertIn("não pode excluir sua própria conta", str(context.exception.detail))
    
    def test_nao_autoexclusao_deve_passar(self):
        """Teste: Admin pode excluir outro usuário"""
        try:
            ValidacaoSeguranca.validar_nao_autoexclusao(self.admin1, self.user_normal)
        except serializers.ValidationError:
            self.fail("Admin deveria poder excluir outro usuário")
    
    def test_nao_autodesativacao_deve_falhar(self):
        """Teste: Usuário não pode desativar própria conta"""
        dados = {'is_active': False}
        
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_nao_autodesativacao(self.admin1, self.admin1, dados)
        
        self.assertIn("não pode desativar sua própria conta", str(context.exception.detail))
    
    def test_nao_autodesativacao_sem_campo_is_active(self):
        """Teste: Sem campo is_active não deve validar"""
        dados = {'first_name': 'Novo Nome'}
        
        try:
            ValidacaoSeguranca.validar_nao_autodesativacao(self.admin1, self.admin1, dados)
        except serializers.ValidationError:
            self.fail("Sem campo is_active não deveria validar")
    
    def test_ultimo_administrador_exclusao_deve_falhar(self):
        """Teste: Não permitir exclusão do último administrador"""
        # GARANTIR que só existe um admin ativo
        # Primeiro, desativar TODOS os outros admins
        admin_groups = Group.objects.filter(name__icontains='admin')
        Usuario.objects.filter(
            groups__in=admin_groups
        ).exclude(id=self.admin1.id).update(is_active=False)
        
        # Verificar que admin1 é o único admin ativo
        admins_ativos = Usuario.objects.filter(
            is_active=True,
            groups__in=admin_groups
        ).distinct()
        
        # DEBUG: Verificar estado antes do teste
        print(f"DEBUG: Total admins ativos: {admins_ativos.count()}")
        print(f"DEBUG: Admin1 ativo: {self.admin1.is_active}")
        
        # Agora deve falhar ao tentar validar exclusão do último admin
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_ultimo_administrador(self.admin1)
        
        self.assertIn("último administrador", str(context.exception.detail))
    
    def test_ultimo_administrador_com_multiplos_admins(self):
        """Teste: Com múltiplos admins, pode desativar um"""
        try:
            ValidacaoSeguranca.validar_ultimo_administrador(self.admin1)
        except serializers.ValidationError:
            self.fail("Com múltiplos admins, deveria poder desativar um")
    
    def test_ultimo_administrador_desativacao_deve_falhar(self):
        """Teste: Não permitir desativação do último administrador"""
        # Desativar admin2
        self.admin2.is_active = False
        self.admin2.save()
        
        dados = {'is_active': False}
        
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_ultimo_administrador(self.admin1, dados)
        
        self.assertIn("último administrador", str(context.exception.detail))
    
    def test_ultimo_administrador_usuario_normal(self):
        """Teste: Usuário normal pode ser desativado mesmo sendo único"""
        try:
            ValidacaoSeguranca.validar_ultimo_administrador(self.user_normal)
        except serializers.ValidationError:
            self.fail("Usuário normal deveria poder ser desativado")
    
    def test_hierarquia_edicao_admin_pode_editar_user(self):
        """Teste: Admin pode editar usuário normal"""
        try:
            ValidacaoSeguranca.validar_hierarquia_edicao(self.admin1, self.user_normal)
        except serializers.ValidationError:
            self.fail("Admin deveria poder editar usuário normal")
    
    def test_hierarquia_edicao_user_nao_pode_editar_admin(self):
        """Teste: Usuário normal não pode editar admin"""
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_hierarquia_edicao(self.user_normal, self.admin1)
        
        self.assertIn("Apenas administradores", str(context.exception.detail))
    
    def test_hierarquia_edicao_proprio_usuario(self):
        """Teste: Usuário pode editar própria conta"""
        try:
            ValidacaoSeguranca.validar_hierarquia_edicao(self.user_normal, self.user_normal)
        except serializers.ValidationError:
            self.fail("Usuário deveria poder editar própria conta")
    
    def test_hierarquia_edicao_superuser(self):
        """Teste: Superuser pode editar qualquer usuário"""
        try:
            ValidacaoSeguranca.validar_hierarquia_edicao(self.superuser, self.admin1)
            ValidacaoSeguranca.validar_hierarquia_edicao(self.superuser, self.user_normal)
        except serializers.ValidationError:
            self.fail("Superuser deveria poder editar qualquer usuário")
    
    def test_edicao_propria_conta_campos_permitidos(self):
        """Teste: Usuário pode editar campos próprios permitidos"""
        dados = {
            'first_name': 'Novo Nome',
            'email': 'novo@email.com',
            'telefone': '11999999999',
            'password': 'nova_senha'
        }
        
        try:
            ValidacaoSeguranca.validar_edicao_propria_conta(self.user_normal, self.user_normal, dados)
        except serializers.ValidationError:
            self.fail("Usuário deveria poder editar campos próprios permitidos")
    
    def test_edicao_propria_conta_campos_proibidos(self):
        """Teste: Usuário não pode editar campos proibidos da própria conta"""
        dados = {
            'is_active': False,
            'groups': [self.grupo_admin.id],
            'is_superuser': True
        }
        
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_edicao_propria_conta(self.user_normal, self.user_normal, dados)
        
        self.assertIn("não pode alterar os campos", str(context.exception.detail))
    
    def test_edicao_outro_usuario_admin(self):
        """Teste: Admin editando outro usuário não tem restrições de campos"""
        dados = {
            'is_active': False,
            'groups': [self.grupo_admin.id]
        }
        
        try:
            ValidacaoSeguranca.validar_edicao_propria_conta(self.admin1, self.user_normal, dados)
        except serializers.ValidationError:
            self.fail("Admin deveria poder editar qualquer campo de outro usuário")
    
    def test_grupos_sensiveis_user_nao_pode_alterar(self):
        """Teste: Usuário normal não pode alterar grupos"""
        dados = {'groups': [self.grupo_admin.id]}
        
        with self.assertRaises(serializers.ValidationError) as context:
            ValidacaoSeguranca.validar_grupos_sensiveis(self.user_normal, self.user_normal, dados)
        
        self.assertIn("Apenas administradores podem alterar grupos", str(context.exception.detail))
    
    def test_grupos_sensiveis_admin_pode_alterar(self):
        """Teste: Admin pode alterar grupos"""
        dados = {'groups': [self.grupo_user.id]}
        
        try:
            ValidacaoSeguranca.validar_grupos_sensiveis(self.admin1, self.user_normal, dados)
        except serializers.ValidationError:
            self.fail("Admin deveria poder alterar grupos")
    
    def test_grupos_sensiveis_sem_campo_groups(self):
        """Teste: Sem campo groups não deve validar"""
        dados = {'first_name': 'Novo Nome'}
        
        try:
            ValidacaoSeguranca.validar_grupos_sensiveis(self.user_normal, self.user_normal, dados)
        except serializers.ValidationError:
            self.fail("Sem campo groups não deveria validar")


class TestValidacaoCompleta(TestCase):
    """Testes para validações integradas"""
    
    def setUp(self):
        """Configuração inicial"""
        self.grupo_admin = Group.objects.create(name='Administradores')
        
        self.admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='teste123'
        )
        self.admin.groups.add(self.grupo_admin)
        
        self.user = Usuario.objects.create_user(
            username='user',
            email='user@test.com',
            password='teste123'
        )
    
    def test_validacao_edicao_completa_sucesso(self):
        """Teste: Validação completa deve passar para dados válidos"""
        dados = {
            'first_name': 'Nome Atualizado',
            'email': 'novo@email.com'
        }
        
        try:
            ValidacaoCompleta.validar_edicao_usuario(self.user, self.user, dados)
        except serializers.ValidationError:
            self.fail("Validação completa deveria passar para dados válidos")
    
    def test_validacao_edicao_completa_falha_autodesativacao(self):
        """Teste: Validação completa deve falhar para autodesativação"""
        dados = {'is_active': False}
        
        with self.assertRaises(serializers.ValidationError):
            ValidacaoCompleta.validar_edicao_usuario(self.user, self.user, dados)
    
    def test_validacao_exclusao_completa_sucesso(self):
        """Teste: Validação de exclusão deve passar para caso válido"""
        try:
            ValidacaoCompleta.validar_exclusao_usuario(self.admin, self.user)
        except serializers.ValidationError:
            self.fail("Validação de exclusão deveria passar para caso válido")
    
    def test_validacao_exclusao_completa_falha_autoexclusao(self):
        """Teste: Validação de exclusão deve falhar para autoexclusão"""
        with self.assertRaises(serializers.ValidationError):
            ValidacaoCompleta.validar_exclusao_usuario(self.admin, self.admin)