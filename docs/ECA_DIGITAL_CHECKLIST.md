# Checklist de Conformidade — ECA Digital (Lei 15.211/2025)

| Campo | Valor |
|-------|-------|
| **Sistema** | deepEdu — Tutor RAG de Matemática (Ensino Médio) |
| **Versão** | 1.0 |
| **Data** | 29/06/2026 |
| **Responsável** | _________________________ |
| **Instituição** | _________________________ |

---

## Instruções

Marque cada item conforme o status: **S** = Sim | **N** = Não | **NA** = Não aplicável | **P** = Parcial (descrever em observações).

Itens marcados **N** ou **P** devem ter plano de ação com prazo na coluna de observações.

**Referência legal:** Lei nº 15.211/2025 (Estatuto Digital da Criança e do Adolescente).

---

## 1. Governança e inventário

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 1.1 | Inventário completo do ecossistema digital (softwares, APIs, fornecedores) documentado | ☐ | ☐ | ☐ | ☐ | |
| 1.2 | Classificação de cada ferramenta pelo critério de "acesso provável" por menores | ☐ | ☐ | ☐ | ☐ | |
| 1.3 | DPIA (Relatório de Impacto à Proteção de Dados) preenchido e aprovado | ☐ | ☐ | ☐ | ☐ | |
| 1.4 | DPO ou encarregado de dados designado e contato publicado | ☐ | ☐ | ☐ | ☐ | |
| 1.5 | Política de privacidade específica para o tutor RAG disponível aos responsáveis | ☐ | ☐ | ☐ | ☐ | |

---

## 2. Consentimento e verificação de idade

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 2.1 | Consentimento parental **granular** (não genérico/guarda-chuva) implementado | ☐ | ☐ | ☐ | ☐ | |
| 2.2 | Registro auditável de consentimento: data, versão dos termos, identificador pseudonimizado | ☐ | ☐ | ☐ | ☐ | |
| 2.3 | Verificação de faixa etária **sem autodeclaração simples** (vínculo escolar/código) | ☐ | ☐ | ☐ | ☐ | |
| 2.4 | Fluxo de recusa de consentimento: sistema não processa dados além de mensagem informativa | ☐ | ☐ | ☐ | ☐ | |
| 2.5 | Mecanismo de opt-out (`SAIR` ou equivalente) funcional e testado | ☐ | ☐ | ☐ | ☐ | |
| 2.6 | Direito de acesso, correção e exclusão de dados implementado | ☐ | ☐ | ☐ | ☐ | |

---

## 3. Tratamento de dados

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 3.1 | Coleta mínima de dados (apenas o necessário para tutoria) | ☐ | ☐ | ☐ | ☐ | |
| 3.2 | Dados pessoais mascarados antes de indexação no RAG (RF27) | ☐ | ☐ | ☐ | ☐ | |
| 3.3 | Histórico de chat com política de retenção definida (padrão: 90 dias) | ☐ | ☐ | ☐ | ☐ | |
| 3.4 | Criptografia em trânsito (HTTPS/TLS) em todos os endpoints | ☐ | ☐ | ☐ | ☐ | |
| 3.5 | Criptografia em repouso para banco de dados e backups | ☐ | ☐ | ☐ | ☐ | |
| 3.6 | **Proibição** de uso de dados para publicidade ou perfilamento comercial | ☐ | ☐ | ☐ | ☐ | |
| 3.7 | **Proibição** de compartilhamento de dados com terceiros sem base legal | ☐ | ☐ | ☐ | ☐ | |

---

## 4. Fornecedores e contratos

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 4.1 | Due diligence de fornecedores (Meta/WhatsApp, LangSmith, hospedagem) documentada | ☐ | ☐ | ☐ | ☐ | |
| 4.2 | Cláusulas contratuais: exclusão de dados ao término da relação | ☐ | ☐ | ☐ | ☐ | |
| 4.3 | Cláusulas contratuais: notificação de incidentes em até 24 horas | ☐ | ☐ | ☐ | ☐ | |
| 4.4 | Cláusulas contratuais: direito de auditoria pela instituição de ensino | ☐ | ☐ | ☐ | ☐ | |
| 4.5 | Fornecedores com privacy by design e proteção por padrão comprovados | ☐ | ☐ | ☐ | ☐ | |

---

## 5. Segurança e incidentes

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 5.1 | Protocolo de resposta a incidentes documentado | ☐ | ☐ | ☐ | ☐ | |
| 5.2 | Registro de incidentes com data, impacto, ação corretiva | ☐ | ☐ | ☐ | ☐ | |
| 5.3 | Validação de assinatura webhook WhatsApp (`X-Hub-Signature-256`) | ☐ | ☐ | ☐ | ☐ | |
| 5.4 | Rate limiting e proteção contra abuso | ☐ | ☐ | ☐ | ☐ | |
| 5.5 | Segredos em variáveis de ambiente (nunca em código-fonte) | ☐ | ☐ | ☐ | ☐ | |
| 5.6 | Teste de restauração de backup realizado nos últimos 90 dias | ☐ | ☐ | ☐ | ☐ | |

---

## 6. Transparência e auditoria

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 6.1 | Citação de fontes nas respostas do tutor (RF29) | ☐ | ☐ | ☐ | ☐ | |
| 6.2 | Traces LangSmith ativos em produção (RF31) | ☐ | ☐ | ☐ | ☐ | |
| 6.3 | Logs de auditoria locais (`audit_log`) conforme `docs/AUDITORIA_ECA.md` | ☐ | ☐ | ☐ | ☐ | |
| 6.4 | **Todo o projeto** auditável — todos os módulos emitem eventos (RF47) | ☐ | ☐ | ☐ | ☐ | |
| 6.5 | Fail-closed: sem log, sem processamento de dados de menor | ☐ | ☐ | ☐ | ☐ | |
| 6.6 | Exportação de relatórios para escola/DPO (`export_audit.py`) | ☐ | ☐ | ☐ | ☐ | |
| 6.7 | Comunicação clara ao usuário sobre registro de conversas (ECA) | ☐ | ☐ | ☐ | ☐ | |
| 6.8 | Canal de contato para dúvidas de privacidade disponível | ☐ | ☐ | ☐ | ☐ | |

---

## 7. Capacitação

| # | Item | S | N | NA | P | Observações / Plano de ação |
|---|------|---|---|----|----|----------------------------|
| 7.1 | Equipe técnica treinada em LGPD e ECA Digital | ☐ | ☐ | ☐ | ☐ | |
| 7.2 | Professores/gestores informados sobre funcionamento e riscos do sistema | ☐ | ☐ | ☐ | ☐ | |
| 7.3 | Material informativo para pais/responsáveis disponibilizado | ☐ | ☐ | ☐ | ☐ | |

---

## Resultado da auditoria

| Métrica | Valor |
|---------|-------|
| Total de itens aplicáveis | _____ |
| Itens conformes (S) | _____ |
| Itens não conformes (N) | _____ |
| Itens parciais (P) | _____ |
| **Percentual de conformidade** | _____% |

**Parecer:** ☐ Aprovado para produção  ☐ Aprovado com ressalvas  ☐ Reprovado

**Assinatura do responsável técnico:** _________________________ **Data:** ___/___/______

**Assinatura do DPO / Encarregado:** _________________________ **Data:** ___/___/______

**Assinatura da gestão escolar:** _________________________ **Data:** ___/___/______
