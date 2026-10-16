# Arquitetura de Auditoria — ECA Digital e LGPD

| Campo | Valor |
|-------|-------|
| **Sistema** | DeepEdu — Tutor RAG de Matemática (Ensino Médio) |
| **Base legal** | Lei 15.211/2025 (ECA Digital) + Lei 13.709/2018 (LGPD) |
| **Versão** | 1.0 |
| **Data** | 29/06/2026 |

---

## 1. Princípio fundamental

> **Todo o projeto é auditável.** Nenhum módulo, canal ou operação que envolva dados de menores pode operar sem rastreio. A escola, o DPO e a ANPD devem poder reconstruir *quem fez o quê, quando, com qual base legal e qual resultado*.

A auditoria não se limita ao LangSmith: é uma **camada transversal** (M09) que cobre fluxo técnico, pedagógico, administrativo e legal.

---

## 2. Escopo da auditabilidade

| Área | O que deve ser auditado | Onde persiste |
|------|-------------------------|---------------|
| **WhatsApp (entrada/saída)** | `message_id`, direção, timestamp, `phone_hash`, consentimento ativo | `audit_log` + LangSmith |
| **Consentimento ECA** | aceite/recusa, versão dos termos, IP/hash | `consent_log` (imutável) |
| **Pipeline RAG** | query, chunks, scores, prompt montado, tokens, resposta | LangSmith + `audit_log` resumo |
| **LLM / SymPy** | modelo, parâmetros, verificação numérica | LangSmith trace |
| **Memória de sessão** | criação, resumo, exclusão (LGPD) | `audit_log` |
| **Corpus (admin)** | upload, delete, reindex, versão do índice | `audit_log` |
| **Dashboard (admin)** | login, ações RBAC (R04–R16) | `audit_log` |
| **Incidentes** | vazamento, acesso indevido, falha de segurança | `incident_log` |
| **Fornecedores** | exportações para Meta, LangSmith | ROPA + logs de integração |

---

## 3. Três camadas de auditoria

```
┌─────────────────────────────────────────────────────────────┐
│  Camada 1 — Logs locais imutáveis (obrigatório, ECA/LGPD)   │
│  audit_log · consent_log · incident_log                       │
│  Retenção: 12 meses (audit) · 5 anos (consent)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Camada 2 — LangSmith (técnico, pipeline RAG)                │
│  Traces completos · pseudonimizado · por ambiente           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Camada 3 — Exportação para auditoria escolar                │
│  Relatórios CSV/JSON · API read-only · papel viewer/DPO     │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Schema do log de auditoria (`audit_log`)

Cada evento **obrigatório** contém:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `event_id` | UUID | Identificador único |
| `timestamp` | ISO 8601 UTC | Momento do evento |
| `correlation_id` | UUID | Liga eventos da mesma requisição |
| `actor_type` | enum | `student`, `admin`, `system`, `webhook` |
| `actor_id` | string | `phone_hash`, `user_id` ou `system` |
| `session_id` | string | Pseudonimizado |
| `action` | string | Ex.: `message.received`, `rag.generate`, `corpus.upload` |
| `resource` | string | Ex.: `chunk:abc123`, `document:apostila.pdf` |
| `outcome` | enum | `success`, `failure`, `abstained`, `denied` |
| `metadata` | JSON | Scores, token counts, `bncc_skill` — **sem PII em claro** |
| `langsmith_run_id` | string | Link para trace (quando aplicável) |

**Regras:**
- Logs **append-only** (sem UPDATE/DELETE)
- PII nunca em claro: usar `phone_hash`, `session_id` pseudonimizado
- Falha ao gravar log → **não processar** a mensagem do menor (fail-closed)

---

## 5. Eventos obrigatórios por módulo

### M01 — WhatsApp
- `webhook.received`, `webhook.signature_invalid`, `message.received`, `message.sent`, `message.duplicate_skipped`

### M02 — Orquestrador
- `rag.started`, `rag.completed`, `rag.abstained`, `rag.failed`, `tokens.budget_exceeded`

### M03 — Memória
- `session.created`, `history.summarized`, `session.deleted` (solicitação LGPD)

### M04 — Retriever
- `retrieval.executed` (top_k, scores, chunk_ids)

### M05 — Gerador
- `llm.invoked`, `sympy.verified`, `sympy.divergence`

### M06/M07 — Ingestão / Índice
- `corpus.document_added`, `corpus.document_removed`, `index.rebuilt`, `index.version_switched`

### M09 — Governança
- `consent.granted`, `consent.revoked`, `optout.requested`
- `admin.login`, `admin.action_denied` (RBAC)
- `incident.reported`

---

## 6. LangSmith (RF31) — complemento, não substituto

| Aspecto | LangSmith | Log local |
|---------|-----------|-----------|
| Finalidade | Debug técnico, qualidade RAG | Conformidade legal ECA/LGPD |
| PII | Proibido nos traces | Apenas hashes |
| Retenção | Política LangChain | 12 meses mínimo |
| Acesso escola | Via export/API | Dashboard + export direto |
| Obrigatório em prod | Sim | **Sim — independente** |

Variáveis obrigatórias:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=deepedu-prod
LANGSMITH_API_KEY=...
```

Tags em cada trace: `session_id`, `phone_hash`, `channel`, `consent_version`, `bncc_skill`.

---

## 7. Transparência para o usuário (ECA Art. 8º e boas práticas)

Na **primeira interação** (RF42), mensagem obrigatória:

> "Olá! Sou o tutor de Matemática da [escola]. Para te ajudar, registro nossas conversas de forma segura, conforme a política de privacidade da escola e a lei de proteção de menores no ambiente digital. Seus pais/responsáveis autorizaram este uso. Para parar, envie SAIR."

O prompt do sistema **não deve** afirmar que conversas são anônimas ou não registradas.

---

## 8. Exportação para auditoria escolar

Endpoint ou script (papel `admin` / DPO):

```bash
python scripts/export_audit.py \
  --from 2026-01-01 --to 2026-06-30 \
  --format csv \
  --output relatorio_auditoria_escola.csv
```

Conteúdo exportável:
- Resumo de consentimentos
- Volume de mensagens por período (sem conteúdo, se política restritiva)
- Ações administrativas
- Incidentes
- Metadados RAG (abstinência, fontes citadas)

Conteúdo de mensagens: apenas com base legal e autorização expressa do DPO.

---

## 9. Direito de auditoria da escola (ECA Digital)

Contrato com a instituição deve garantir:
- Acesso a logs e relatórios mediante solicitação
- Notificação de incidentes em **24 horas**
- Suporte a fiscalização da ANPD
- Exclusão de dados ao término do contrato com comprovante

Ver checklist: `docs/ECA_DIGITAL_CHECKLIST.md` itens 4.3, 4.4, 6.3.

---

## 10. Testes de aceitação (auditoria)

| ID | Teste | Critério |
|----|-------|----------|
| AU-01 | Mensagem WhatsApp processada | ≥ 1 evento em `audit_log` + trace LangSmith |
| AU-02 | Consentimento negado | Nenhum evento `rag.*`; apenas `consent.revoked` |
| AU-03 | Upload de corpus | `corpus.document_added` com `user_id` |
| AU-04 | Falha de gravação de log | Mensagem **não** processada (fail-closed) |
| AU-05 | Exportação 30 dias | CSV gerado sem PII em claro |
| AU-06 | Exclusão LGPD (`SAIR`) | `session.deleted` + dados removidos |
| AU-07 | Ação RBAC negada | `admin.action_denied` registrado |

---

## 11. Responsabilidades

| Papel | Responsabilidade |
|-------|------------------|
| Desenvolvimento | Implementar `audit_log` em todos os módulos |
| DPO | Validar ROPA, DPIA, exportações |
| Escola | Auditoria periódica, contratos com fornecedores |
| Operação | Monitorar incidentes, backups de logs |

---

## 12. Referências cruzadas

- RF30 — Privacidade LGPD
- RF31 — LangSmith
- RF32 — ECA Digital
- RF42 — Consentimento
- RF46 — Orçamento de tokens (registrar tokens no audit)
- `docs/ROPA.md`
- `docs/ECA_DIGITAL_CHECKLIST.md`
- `docs/RBAC.md` — R13 `audit.logs`
