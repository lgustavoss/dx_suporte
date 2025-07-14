
# Copilot Instructions – DX Suporte

## Estrutura de Diretórios

- **Backend:** `backend/` (Django + DRF, apps em `backend/apps/`)
- **Frontend:** `frontend/` (React + Vite, código em `frontend/src/`)

## Arquitetura e Fluxos

- O backend segue arquitetura Django modularizada:  
  - `accounts/` (usuários/autenticação),  
  - `controle_acesso/` (grupos/permissões),  
  - `core/` (filtros, paginação, integrações),  
  - `endpoints/v1/` (centralização de rotas).
- O frontend utiliza React com componentes funcionais, hooks customizados e organização por domínio (ex: `pages/perfil/`, `hooks/usePerfil.js`).

## Convenções e Padrões

- **Erros:**  
  Não usar `alert` ou `toast.error(err.message)` diretamente.  
  Use o hook `useErrorHandler` e a função `showError` para exibir erros ao usuário.  
  Exemplo:  
  ```js
  import { useErrorHandler } from "../hooks/useErrorHandler";
  const { showError } = useErrorHandler();
  // ...
  try { ... } catch (err) { showError(err); }
  ```
- **Máscaras:**  
  Use `maskTelefone` de `src/utils/mask.js` para campos de telefone.
- **Status:**  
  Use o componente `BadgeStatus` para exibir status booleanos (ex: ativo/online).
- **Containers:**  
  Use `PageContainer` para páginas principais.

## Integração Frontend/Backend

- O frontend consome a API REST do backend, com base em `API_BASE_URL` definido em `src/services/api.js`.
- Autenticação JWT: tokens são armazenados no `localStorage` e enviados no header `Authorization`.
- Serviços de usuário centralizados em `src/services/userService.js` (fetch/update de perfil).

## Fluxos de Desenvolvimento

- **Backend:**  
  - Ative o ambiente virtual, instale dependências (`pip install -r requirements.txt`), configure `.env` e rode `python manage.py runserver`.
  - Sincronize permissões com `sync_permissions` via shell Django.
- **Frontend:**  
  - Use `npm install` e `npm run dev` para desenvolvimento local.
- **Testes:**  
  - Backend: utilize `pytest` ou `python manage.py test` (testes em `apps/*/tests/`).
  - Frontend: siga padrões do React Testing Library (não há testes presentes por padrão).

## Exemplos de Padrão

- Exibir erro:
  ```js
  catch (err) { showError(err); }
  ```
- Atualizar perfil:
  ```js
  await updatePerfil(user.id, payload);
  ```

> Sempre siga a estrutura e os padrões acima ao criar novos componentes, hooks ou endpoints.