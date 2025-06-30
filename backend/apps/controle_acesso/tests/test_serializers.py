from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError

from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado
from controle_acesso.serializers import (
    PermissaoCustomizadaSerializer,
    GrupoCustomizadoSerializer
)

Usuario = get_user_model()


class TestPermissaoCustomizadaSerializer(TestCase):
    """Testes para PermissaoCustomizadaSerializer"""
    
    def setUp(self):
        """Configuração inicial"""
        self.factory = APIRequestFactory()
        
        self.permissao = PermissaoCustomizada.objects.create(
            modulo='test',
            acao='serializer',
            nome='test_serializer',
            descricao='Teste do serializer',
            ativo=True
        )
    
    def test_serializar_permissao(self):
        """Teste: Serialização de permissão existente"""
        serializer = PermissaoCustomizadaSerializer(self.permissao)
        data = serializer.data
        
        self.assertEqual(data['modulo'], 'test')
        self.assertEqual(data['acao'], 'serializer')
        self.assertEqual(data['nome'], 'test_serializer')
        self.assertEqual(data['descricao'], 'Teste do serializer')
        self.assertTrue(data['ativo'])
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_criar_permissao_via_serializer(self):
        """Teste: Criar nova permissão via serializer"""
        data = {
            'modulo': 'novo',
            'acao': 'criar',
            'nome': 'novo_criar',
            'descricao': 'Nova permissão criada',
            'ativo': True
        }
        
        serializer = PermissaoCustomizadaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        permissao = serializer.save()
        self.assertEqual(permissao.nome, 'novo_criar')
        self.assertTrue(permissao.ativo)
    
    def test_validacao_nome_obrigatorio(self):
        """Teste: Nome é obrigatório"""
        data = {
            'modulo': 'test',
            'acao': 'falhar',
            # 'nome': FALTANDO
            'descricao': 'Deve falhar',
            'ativo': True
        }
        
        serializer = PermissaoCustomizadaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('nome', serializer.errors)
    
    def test_validacao_nome_unico(self):
        """Teste: Nome deve ser único"""
        data = {
            'modulo': 'test',
            'acao': 'duplicar',
            'nome': 'test_serializer',  # ← Nome já existe
            'descricao': 'Tentativa de duplicação',
            'ativo': True
        }
        
        serializer = PermissaoCustomizadaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('nome', serializer.errors)
    
    def test_atualizar_permissao_existente(self):
        """Teste: Atualizar permissão existente"""
        data = {
            'modulo': 'test',
            'acao': 'serializer',
            'nome': 'test_serializer',
            'descricao': 'Descrição atualizada via serializer',
            'ativo': False  # ← Mudando de True para False
        }
        
        serializer = PermissaoCustomizadaSerializer(
            self.permissao, 
            data=data
        )
        self.assertTrue(serializer.is_valid())
        
        permissao_atualizada = serializer.save()
        self.assertEqual(
            permissao_atualizada.descricao, 
            'Descrição atualizada via serializer'
        )
        self.assertFalse(permissao_atualizada.ativo)
    
    def test_campos_readonly(self):
        """Teste: Campos readonly não são alteráveis via data"""
        original_created = self.permissao.created_at
        
        data = {
            'modulo': 'test',
            'acao': 'serializer',
            'nome': 'test_serializer',
            'descricao': 'Tentando alterar timestamps',
            'ativo': True,
            'created_at': '2020-01-01T00:00:00Z',  # ← Tentativa de alterar
            'updated_at': '2020-01-01T00:00:00Z'   # ← Tentativa de alterar
        }
        
        serializer = PermissaoCustomizadaSerializer(
            self.permissao,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        
        permissao_atualizada = serializer.save()
        
        # Timestamps não devem ter sido alterados via data
        self.assertEqual(permissao_atualizada.created_at, original_created)
        self.assertNotEqual(
            str(permissao_atualizada.created_at), 
            '2020-01-01T00:00:00Z'
        )


class TestGrupoCustomizadoSerializer(TestCase):
    """Testes para GrupoCustomizadoSerializer"""
    
    def setUp(self):
        """Configuração inicial"""
        # Criar grupo Django único para testes
        self.grupo_django = Group.objects.create(name='TestGroup_Serializer_Único')
        
        # Criar grupo customizado
        self.grupo_customizado = GrupoCustomizado.objects.create(
            group=self.grupo_django,
            descricao='Descrição do grupo de teste',
            ativo=True
        )
    
    def test_criar_grupo_via_serializer(self):
        """Teste: Criar novo grupo via serializer"""
        # ✅ USAR FORMATO CORRETO
        data = {
            'group_data': {  # ← CORRIGIDO
                'name': 'TestGroup_Criar_Serializer_Único'  # Nome único
            },
            'descricao': 'Grupo para teste de serializer',
            'ativo': True
        }
        
        serializer = GrupoCustomizadoSerializer(data=data)
        
        # Debug se falhar
        if not serializer.is_valid():
            print(f"Erros do serializer: {serializer.errors}")
        
        self.assertTrue(serializer.is_valid(), f"Erros: {serializer.errors}")
        
        grupo = serializer.save()
        
        self.assertEqual(grupo.group.name, 'TestGroup_Criar_Serializer_Único')
        self.assertEqual(grupo.descricao, 'Grupo para teste de serializer')

    def test_descricao_pode_ser_vazia(self):
        """Teste: Descrição pode ser vazia"""
        data = {
            'group_data': {  # ← CORRIGIDO
                'name': 'TestGroup_Descricao_Vazia_Único'
            },
            'ativo': True
            # Sem descrição
        }
        
        serializer = GrupoCustomizadoSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), f"Erros: {serializer.errors}")
        
        grupo = serializer.save()
        
        self.assertEqual(grupo.group.name, 'TestGroup_Descricao_Vazia_Único')
        self.assertEqual(grupo.descricao, None)

    def test_serializar_grupo(self):
        """Teste: Serialização de grupo existente"""
        serializer = GrupoCustomizadoSerializer(self.grupo_customizado)
        data = serializer.data
        
        # ✅ CORRIGIR: Agora group é um objeto, não ID
        self.assertEqual(data['group']['id'], self.grupo_django.id)
        self.assertEqual(data['group']['name'], self.grupo_django.name)
        self.assertEqual(data['descricao'], 'Descrição do grupo de teste')
        
        # Verificar se group_id está presente para compatibilidade
        self.assertEqual(data['group_id'], self.grupo_django.id)

    def test_validacao_group_obrigatorio(self):
        """Teste: group_data é obrigatório para criação"""
        data = {
            # ✅ SEM group_data para testar validação
            'descricao': 'Teste sem group_data'
        }
        
        serializer = GrupoCustomizadoSerializer(data=data)
        
        # A validação falha na criação, não na validação inicial
        self.assertTrue(serializer.is_valid())  # Passa na validação
        
        # Mas falha ao salvar
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_atualizar_grupo_existente(self):
        """Teste: Atualizar grupo existente"""
        data = {
            'group_data': {
                'name': 'TestGroup_Atualizado_Único'
            },
            'descricao': 'Descrição atualizada'
        }
        
        serializer = GrupoCustomizadoSerializer(
            self.grupo_customizado, 
            data=data, 
            partial=True
        )
        
        self.assertTrue(serializer.is_valid(), f"Erros: {serializer.errors}")
        
        grupo_atualizado = serializer.save()
        
        self.assertEqual(grupo_atualizado.group.name, 'TestGroup_Atualizado_Único')
        self.assertEqual(grupo_atualizado.descricao, 'Descrição atualizada')

class TestSerializersIntegracao(TestCase):
    """Testes de integração entre serializers"""
    
    def setUp(self):
        """Configuração inicial"""
        pass  # Não criar nada aqui para evitar conflitos
    
    def test_criar_permissao_e_grupo_integrados(self):
        """Teste: Criar permissão e grupo que funcionam juntos"""
        # Criar permissão
        perm_data = {
            'modulo': 'test_integracao',
            'acao': 'testar',
            'nome': 'test_integracao_testar',
            'descricao': 'Teste de integração',
            'ativo': True
        }
        
        permissao_serializer = PermissaoCustomizadaSerializer(data=perm_data)
        self.assertTrue(permissao_serializer.is_valid())
        permissao = permissao_serializer.save()
        
        # Criar grupo
        grupo_data = {
            'group_data': {
                'name': 'Grupo_Integracao_Único'
            },
            'descricao': 'Grupo para teste de integração',
            'ativo': True
        }
        
        grupo_serializer = GrupoCustomizadoSerializer(data=grupo_data)
        
        self.assertTrue(grupo_serializer.is_valid(), f"Erros: {grupo_serializer.errors}")
        
        grupo = grupo_serializer.save()
        
        # Verificar se ambos foram criados corretamente
        self.assertEqual(permissao.nome, 'test_integracao_testar')
        self.assertEqual(grupo.group.name, 'Grupo_Integracao_Único')