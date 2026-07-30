# Registro de Operações de Tratamento (ROPA) — LGPD Art. 37

| Campo | Valor |
|-------|-------|
| **Controlador** | _________________________ (Instituição de Ensino) |
| **Operador** | _________________________ (Responsável técnico / deepEdu) |
| **Encarregado (DPO)** | _________________________ |
| **Contato DPO** | _________________________ |
| **Versão** | 1.0 |
| **Data** | 29/06/2026 |
| **Revisão prevista** | Trimestral |

---

## 1. Identificação do tratamento

| Campo | Descrição |
|-------|-----------|
| **Nome do sistema** | deepEdu — Tutor RAG de Matemática para Ensino Médio |
| **Finalidade** | Tutoria personalizada em Matemática via WhatsApp, com recuperação de conteúdo curricular indexado |
| **Base legal (LGPD)** | Consentimento do responsável legal (Art. 7º, I) + Legítimo interesse educacional com salvaguardas (Art. 7º, IX), em conformidade com ECA Digital |
| **Categorias de titulares** | Estudantes do Ensino Médio (15–17 anos), menores de idade |
| **Prazo de retenção** | Histórico de chat: 90 dias (configurável). Logs de auditoria: 12 meses. Consentimentos: 5 anos após término da relação. |

---

## 2. Dados pessoais tratados

| Categoria | Dados | Obrigatório | Finalidade |
|-----------|-------|:-----------:|------------|
| Identificação | Número de telefone (WhatsApp) | Sim | Canal de comunicação e sessão |
| Identificação | Código escolar / matrícula (hash) | Não | Verificação de vínculo e idade |
| Conteúdo | Mensagens enviadas pelo estudante | Sim | Processamento RAG e tutoria |
| Conteúdo | Respostas geradas pelo sistema | Sim | Prestação do serviço |
| Técnico | session_id, timestamps, message_id | Sim | Funcionamento, auditoria, idempotência |
| Técnico | IP do webhook (Meta) | Sim | Segurança e logs |
| Consentimento | Registro de aceite/recusa de termos | Sim | Conformidade LGPD/ECA Digital |

**Dados sensíveis:** O sistema **não deve** coletar dados sensíveis (saúde, origem racial, biometria etc.). Mensagens com conteúdo sensível acidental devem ser mascaradas (RF27).

---

## 3. Operações de tratamento

| # | Operação | Descrição | Base legal |
|---|----------|-----------|------------|
| 1 | Coleta | Recebimento de mensagem via webhook WhatsApp | Consentimento |
| 2 | Armazenamento | Persistência de histórico de sessão e consentimento | Consentimento + execução de contrato |
| 3 | Processamento | Embedding da pergunta, retrieval, geração LLM | Execução de contrato |
| 4 | Compartilhamento | Envio de traces ao LangSmith (pseudonimizado) | Legítimo interesse (auditoria técnica) |
| 5 | Compartilhamento | API WhatsApp (Meta) para envio de resposta | Execução de contrato |
| 6 | Eliminação | Exclusão por solicitação ou expiração de retenção | Obrigação legal (LGPD Art. 18) |
| 7 | Anonimização | Mascaramento de PII antes de indexação no corpus | Legítimo interesse |

---

## 4. Fluxo de dados

```
Estudante (WhatsApp)
    → Meta Cloud API (webhook HTTPS)
    → deepEdu API (validação, fila)
    → Worker (RAG: retrieval + LLM)
    → Banco vetorial (Qdrant) — apenas corpus curricular, sem PII
    → Banco de sessões (PostgreSQL/SQLite) — histórico pseudonimizado
    → LangSmith (traces técnicos)
    → Meta Cloud API (resposta ao estudante)
```

---

## 5. Compartilhamento com terceiros

| Terceiro | Dados compartilhados | Finalidade | País | Garantias |
|----------|---------------------|------------|------|-----------|
| Meta (WhatsApp) | Telefone, mensagens | Entrega de mensagens | EUA | DPA, cláusulas contratuais |
| LangSmith (LangChain) | Traces pseudonimizados | Auditoria e debugging | EUA | Opt-out de PII nos traces |
| Provedor de hospedagem | Dados em repouso | Infraestrutura | _____ | Contrato + criptografia |

**Não há** compartilhamento para fins publicitários ou perfilamento.

---

## 6. Medidas de segurança

| Medida | Implementação |
|--------|---------------|
| Criptografia em trânsito | TLS 1.2+ em todos os endpoints |
| Criptografia em repouso | Volume criptografado / banco com TDE |
| Controle de acesso | RBAC (ver `docs/RBAC.md`) |
| Pseudonimização | phone_hash, session_id sem nome |
| Mascaramento na indexação | RF27 — CPF, e-mail, telefone → `[REDACTED]` |
| Backup | Diário, criptografado, retenção 30 dias |
| Teste de restore | Trimestral |

---

## 7. Direitos dos titulares (LGPD Art. 18)

| Direito | Como exercer | Prazo de resposta |
|---------|--------------|-------------------|
| Confirmação de tratamento | E-mail ao DPO | 15 dias |
| Acesso aos dados | E-mail ao DPO | 15 dias |
| Correção | E-mail ao DPO | 15 dias |
| Eliminação | E-mail ao DPO ou comando `SAIR` no WhatsApp | 15 dias |
| Portabilidade | Exportação JSON sob solicitação | 15 dias |
| Revogação de consentimento | Comando `SAIR` ou e-mail ao DPO | Imediato (cessa tratamento) |

---

## 8. Transferência internacional

| Destinatário | Mecanismo | Status |
|--------------|-----------|--------|
| Meta (WhatsApp Cloud API) | Cláusulas contratuais padrão / DPA | ☐ Verificado |
| LangSmith | Avaliar localização de dados / DPA | ☐ Verificado |

---

## 9. Avaliação de risco

| Risco | Probabilidade | Impacto | Mitigação |
|-------|:-------------:|:-------:|-----------|
| Vazamento de histórico de chat | Média | Alto | Criptografia, RBAC, retenção limitada |
| Resposta incorreta em avaliação | Alta | Médio | Modo tutor (RF43), citação de fontes |
| Coleta excessiva de dados | Baixa | Alto | Coleta mínima, revisão trimestral ROPA |
| Acesso não autorizado ao dashboard | Baixa | Alto | RBAC, API Key, HTTPS |
| Uso indevido por terceiros (webhook) | Baixa | Alto | Validação HMAC, rate limit |

---

## 10. Histórico de revisões

| Versão | Data | Responsável | Alteração |
|--------|------|-------------|-----------|
| 1.0 | 29/06/2026 | | Versão inicial |

**Próxima revisão:** ___/___/______
