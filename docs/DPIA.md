# Avaliação de Impacto à Proteção de Dados (DPIA) — DeepEdu

| Campo | Valor |
|-------|-------|
| **Sistema** | DeepEdu — Tutor RAG de Matemática EM |
| **Controlador** | Instituição de Ensino contratante |
| **Operador técnico** | Equipe responsável pelo DeepEdu |
| **Versão** | 1.0 |
| **Data** | 29/06/2026 |
| **Base legal** | LGPD Art. 38 + ECA Digital (Lei 15.211/2025) |

---

## 1. Descrição do tratamento

Tutoria automatizada em Matemática via WhatsApp para estudantes de 15–17 anos, com recuperação de conteúdo curricular indexado (RAG), memória de sessão pseudonimizada e auditoria integral.

---

## 2. Necessidade e proporcionalidade

| Pergunta | Resposta |
|----------|----------|
| O tratamento é necessário? | Sim — prestação do serviço educacional contratado |
| Existe alternativa menos invasiva? | Canal web autenticado; WhatsApp escolhido por acessibilidade |
| Dados minimizados? | Sim — apenas telefone, mensagens e metadados técnicos |
| Retenção limitada? | Sim — ver `docs/ROPA.md` |

---

## 3. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação implementada |
|-------|---------|---------------|------------------------|
| Vazamento de telefone | Alto | Baixa | `phone_hash` + vault Fernet (`phone_vault`) |
| Processamento sem consentimento | Alto | Média | Fluxo ECA: enroll → VINCULAR → ACEITO |
| Falha de auditoria | Alto | Baixa | Fail-closed (`AUDIT_FAIL_CLOSED=true`) |
| Resposta inadequada a menor | Médio | Média | Abstinência RAG (RF37), prompt pedagógico |
| Acesso admin indevido | Alto | Baixa | `ADMIN_API_KEY` + RBAC (`docs/RBAC.md`) |
| Perda de dados | Médio | Baixa | `scripts/backup_data.sh` (RNF16) |

---

## 4. Direitos dos titulares

| Direito | Como exercer |
|---------|--------------|
| Acesso | Solicitar ao DPO da escola |
| Correção | Atualização cadastral via admin |
| Eliminação | Comando `SAIR` + procedimento DPO |
| Portabilidade | Exportação de histórico sob demanda |
| Revogação | `SAIR` revoga consentimento imediatamente |

---

## 5. Conclusão

O tratamento é **admissível** desde que: (1) consentimento parental documentado; (2) segredos de produção configurados; (3) ROPA e este DPIA assinados pelo controlador e DPO.

**Aprovação DPO:** _________________________ Data: ___/___/______
