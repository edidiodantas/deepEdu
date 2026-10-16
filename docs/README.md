# Documentação — DeepEdu

> **Implementação / sequência:** comece por **[`SEQUENCIA_IMPLEMENTACAO.md`](SEQUENCIA_IMPLEMENTACAO.md)** (fonte da verdade) ou pelo atalho na raiz [`../IMPLEMENTACAO.md`](../IMPLEMENTACAO.md).

## Documento principal (impressão / PDF)

| Arquivo | Descrição |
|---------|-----------|
| **[output/DOCUMENTO_FINAL.pdf](output/DOCUMENTO_FINAL.pdf)** | Documento consolidado **v3.0** (requisitos + casos de uso + conformidade) |
| [output/DOCUMENTO_FINAL.html](output/DOCUMENTO_FINAL.html) | Versão HTML do mesmo conteúdo |

**Regenerar PDF:**
```bash
python scripts/build_documento_pdf.py
```

---

## Documentos individuais

| Arquivo | Conteúdo |
|---------|----------|
| **[SEQUENCIA_IMPLEMENTACAO.md](SEQUENCIA_IMPLEMENTACAO.md)** | **★ FONTE DA VERDADE:** ordem S0→S9, chats, prompts, critérios de avanço |
| **[PLANO_ESTE_PC.md](PLANO_ESTE_PC.md)** | **Este PC:** RAG com Amadeus-Verbo (Hugging Face PT-BR) → Ubuntu Server |
| **[CONTROLE_MODULOS.md](CONTROLE_MODULOS.md)** | **Painel vivo:** status por módulo, pendências, chat coordenador |
| **[LOCAL_VS_NUVEM.md](LOCAL_VS_NUVEM.md)** | **Localhost × nuvem:** módulos iguais? sequência S0–S9, sem GPU |
| **[INSTALACAO_INFRAESTRUTURA.md](INSTALACAO_INFRAESTRUTURA.md)** | **Hardware + instalação passo a passo (Ubuntu Server LTS)** — incl. **Fase 0 detalhada** (domínio, LangSmith, Twilio, Asaas, `ADMIN_API_KEY`: para que serve + como obter) |
| [REQUISITOS.md](REQUISITOS.md) | RF01–RF47, RNF01–RNF17, matriz de rastreabilidade |
| [CASOS_DE_USO.md](CASOS_DE_USO.md) | **64 casos de uso** (UC-RF01…47 + UC-RNF01…17) |
| [REVISAO_IMPLEMENTACAO.md](REVISAO_IMPLEMENTACAO.md) | Revisão v3.0 — **sem pendências** |
| [AUDITORIA_ECA.md](AUDITORIA_ECA.md) | Auditoria integral — ECA Digital + LGPD |
| [ECA_DIGITAL_CHECKLIST.md](ECA_DIGITAL_CHECKLIST.md) | Checklist Lei 15.211/2025 |
| [DPIA.md](DPIA.md) | Avaliação de impacto à proteção de dados |
| [SEGURANCA_DADOS.md](SEGURANCA_DADOS.md) | Criptografia em repouso e backup |
| [RBAC.md](RBAC.md) | Matriz de controle de acesso |
| [ROPA.md](ROPA.md) | Registro de operações LGPD |
| [TOKEN_BUDGET.md](TOKEN_BUDGET.md) | Orçamento de tokens Qwen2.5-Math 4K |
| [eval/README.md](eval/README.md) | Guia do dataset de avaliação RAG |
| [eval/dataset_rag_matematica_em.csv](eval/dataset_rag_matematica_em.csv) | **50 perguntas ativas** (EM-001 a EM-050) |

---

## Estrutura do documento final (PDF v3.0)

1. Capa e sumário
2. Parte I — Requisitos (RF/RNF)
3. Parte II — Orçamento de tokens
4. Parte III — Auditoria ECA
5. Parte IV — Revisão de implementação
6. Parte V — **Casos de uso (RF e RNF)**
7. Parte VI — Checklist ECA Digital
8. Parte VII — RBAC
9. Parte VIII — ROPA
10. Parte IX — DPIA
11. Parte X — Segurança de dados
12. Parte XI — Avaliação RAG
13. Anexos A (dataset) e B (prompts)
14. Termo de aprovação
