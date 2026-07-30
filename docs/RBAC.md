# Matriz de Controle de Acesso (RBAC) — deepEdu

| Campo | Valor |
|-------|-------|
| **Sistema** | deepEdu — Tutor RAG de Matemática (Ensino Médio) |
| **Versão** | 1.0 |
| **Data** | 29/06/2026 |

---

## 1. Papéis (roles)

| Papel | Descrição | Público típico |
|-------|-----------|----------------|
| **admin** | Acesso total ao sistema, configuração e governança | TI da escola, desenvolvedor |
| **operator** | Gestão operacional: corpus, reindexação, monitoramento | Coordenador pedagógico, suporte |
| **viewer** | Somente leitura: métricas, logs, visualização de chunks | Professor, gestor |

---

## 2. Recursos do sistema

| ID | Recurso | Descrição |
|----|---------|-----------|
| R01 | `chat.test` | Interface web de chat de teste |
| R02 | `dashboard.metrics` | Métricas e status dos serviços |
| R03 | `corpus.list` | Listar documentos indexados |
| R04 | `corpus.upload` | Upload de novos materiais |
| R05 | `corpus.delete` | Remover documentos do índice |
| R06 | `corpus.reindex` | Disparar reindexação |
| R07 | `chunks.view` | Visualizar chunks e metadados |
| R08 | `sessions.view` | Visualizar sessões de chat (pseudonimizadas) |
| R09 | `sessions.delete` | Excluir dados de sessão (LGPD) |
| R10 | `config.read` | Ler configurações do sistema |
| R11 | `config.write` | Alterar configurações (prompts, limiares) |
| R12 | `users.manage` | Gerenciar usuários e papéis |
| R13 | `audit.logs` | Acessar logs de auditoria |
| R14 | `langsmith.link` | Acessar traces no LangSmith |
| R15 | `eval.run` | Executar avaliação RAG |
| R16 | `whatsapp.config` | Configurar webhook e templates |

---

## 3. Matriz de permissões

| Recurso | admin | operator | viewer |
|---------|:-----:|:--------:|:------:|
| R01 `chat.test` | ✅ | ✅ | ❌ |
| R02 `dashboard.metrics` | ✅ | ✅ | ✅ |
| R03 `corpus.list` | ✅ | ✅ | ✅ |
| R04 `corpus.upload` | ✅ | ✅ | ❌ |
| R05 `corpus.delete` | ✅ | ❌ | ❌ |
| R06 `corpus.reindex` | ✅ | ✅ | ❌ |
| R07 `chunks.view` | ✅ | ✅ | ✅ |
| R08 `sessions.view` | ✅ | ✅ | ❌ |
| R09 `sessions.delete` | ✅ | ❌ | ❌ |
| R10 `config.read` | ✅ | ✅ | ❌ |
| R11 `config.write` | ✅ | ❌ | ❌ |
| R12 `users.manage` | ✅ | ❌ | ❌ |
| R13 `audit.logs` | ✅ | ✅ | ❌ |
| R14 `langsmith.link` | ✅ | ✅ | ❌ |
| R15 `eval.run` | ✅ | ✅ | ❌ |
| R16 `whatsapp.config` | ✅ | ❌ | ❌ |

**Legenda:** ✅ = permitido | ❌ = negado

---

## 4. Autenticação

| Canal | Método | Observação |
|-------|--------|------------|
| Dashboard web | API Key (`ADMIN_API_KEY`) ou OAuth2 | Sessão com timeout de 8h |
| API interna | Header `Authorization: Bearer <token>` | Tokens com escopo por papel |
| WhatsApp | Número de telefone + consentimento (RF42) | Não é RBAC administrativo |

---

## 5. Regras adicionais

1. **Princípio do menor privilégio:** usuários recebem o papel mínimo necessário.
2. **Separação de ambientes:** credenciais de produção não funcionam em desenvolvimento.
3. **Revogação:** desativar usuário remove acesso imediatamente (tokens invalidados).
4. **Auditoria:** toda ação em R04–R12, R15, R16 gera log com `user_id`, `action`, `timestamp`.
5. **Dados de menores:** `sessions.view` exibe apenas `session_id` pseudonimizado, nunca nome completo.

---

## 6. Procedimento de concessão de acesso

1. Solicitação formal à gestão/TI com justificativa e papel desejado.
2. Aprovação do admin ou gestor escolar.
3. Criação de credencial com papel atribuído.
4. Registro em log de auditoria.
5. Revisão trimestral de acessos ativos.

---

## 7. Registro de usuários (modelo)

| user_id | Nome | Papel | Criado em | Último acesso | Status |
|---------|------|-------|-----------|---------------|--------|
| | | | | | ativo/inativo |
