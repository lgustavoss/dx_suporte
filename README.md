# 🏢 DX Suporte - Sistema de Controle de Acesso e Suporte

Sistema completo para gerenciamento de usuários, controle de acesso e suporte ao cliente.

## 🚀 Funcionalidades Implementadas

### ✅ Sistema de Autenticação
- Login com JWT (email + senha)
- Refresh token automático  
- Logout com blacklist de tokens
- Status online/offline em tempo real

### ✅ Gestão de Usuários
- CRUD completo de usuários
- Validação de senha condicional
- Campos customizados (telefone, última atividade)
- Filtros e busca avançada

### ✅ Sistema de Permissões
- Permissões granulares por módulo/ação
- Grupos customizados
- Verificação automática em endpoints
- 8 permissões base implementadas

### ✅ Funcionalidades Avançadas
- Paginação customizada
- Busca global por palavra-chave
- Filtros específicos (status, data, etc.)
- Ordenação por múltiplos campos

## 📊 Endpoints Disponíveis

### 🔐 Autenticação
```http
POST   /api/v1/auth/login/
POST   /api/v1/auth/refresh/
POST   /api/v1/auth/logout/
GET    /api/v1/auth/status-online/
GET    /api/v1/auth/minhas-permissoes/
```

### 👤 Usuários
```http
GET    /api/v1/auth/usuarios/           # Lista com paginação + filtros
POST   /api/v1/auth/usuarios/           # Criar usuário
GET    /api/v1/auth/usuarios/{id}/      # Detalhes do usuário
PATCH  /api/v1/auth/usuarios/{id}/      # Editar + alterar senha
DELETE /api/v1/auth/usuarios/{id}/      # Excluir usuário
GET    /api/v1/auth/usuarios/{id}/grupos/ # Grupos do usuário
```

### 🔧 Controle de Acesso
```http
GET/POST   /api/v1/controle-acesso/grupos/
GET        /api/v1/controle-acesso/permissoes/
POST       /api/v1/controle-acesso/permissoes/sync/
GET/POST   /api/v1/controle-acesso/grupos/{id}/usuarios/
DELETE     /api/v1/controle-acesso/grupos/{id}/usuarios/{user_id}/
GET/POST   /api/v1/controle-acesso/grupos/{id}/permissoes/
DELETE     /api/v1/controle-acesso/grupos/{id}/permissoes/{perm_id}/
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12 + Django 5.1 + DRF
- **Autenticação:** JWT com djangorestframework-simplejwt
- **Banco:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Filtros:** django-filter + filtros customizados
- **Paginação:** Paginação customizada com metadados

## 🏗️ Arquitetura

```
backend/
├── apps/
│   ├── accounts/           # Usuários e autenticação
│   ├── controle_acesso/    # Grupos e permissões
│   ├── core/              # Filtros, paginação, utils
│   └── endpoints/v1/       # Centralização das rotas
```

## 🚀 Como Executar

### 1. Clonar o repositório
```bash
git clone https://github.com/lgustavoss/dx_suporte.git
cd dx_suporte
```

### 2. Criar ambiente virtual
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Sincronizar permissões
```bash
python manage.py shell
>>> from controle_acesso.utils import sync_permissions
>>> sync_permissions()
```

### 6. Executar servidor
```bash
python manage.py runserver
```

## 📋 Roadmap

### ✅ Fase 1 - Base (Concluída)
- Sistema de autenticação
- CRUD de usuários  
- Controle de permissões
- Filtros e paginação

### 🔄 Fase 2 - Validações (Em andamento)
- Validações de negócio
- Sistema de auditoria
- Dashboard básico

### 📅 Fase 3 - Módulos (Planejado)
- Módulo Clientes
- Módulo Contatos  
- Módulo Configurações
- Módulo Chamados
- Módulo Chat/WhatsApp

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Luis Gustavo**
- GitHub: [@lgustavoss](https://github.com/lgustavoss)