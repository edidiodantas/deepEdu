# Sequência oficial de implementação — deepEdu

| Campo | Valor |
|-------|-------|
| **Documento** | **FONTE DA VERDADE** do sequenciamento (não pule etapas) |
| **Projeto** | `/home/Edidio/Projects/deepEdu` |
| **Versão** | 1.0 |
| **Data** | 22/07/2026 |
| **Público** | Você + qualquer agente Cursor em chats separados |

> Se houver dúvida entre este arquivo e outro doc, **este manda na ordem**. Os outros detalham (infra, RF, status).

---

## 0. Mapa rápido — o que ler e quando

| Ordem de leitura | Arquivo | Para quê |
|------------------|---------|----------|
| **1º (este)** | `docs/SEQUENCIA_IMPLEMENTACAO.md` | Ordem oficial S0→S9 + chats |
| 2º | `docs/LOCAL_VS_NUVEM.md` | Localhost = nuvem? (sim no código) |
| 3º | `docs/INSTALACAO_INFRAESTRUTURA.md` | Hardware + instalação Ubuntu + Fase 0 (contas) |
| 4º | `docs/CONTROLE_MODULOS.md` | Status vivo, pendências, chat coordenador |
| 5º | `docs/REQUISITOS.md` | RF/RNF detalhados (só o módulo do chat) |
| Apoio | `docs/TOKEN_BUDGET.md`, `docs/AUDITORIA_ECA.md`, `docs/eval/` | Tokens, ECA, dataset |

Índice geral: `docs/README.md`.

---

## 1. Decisões já fechadas (não reabrir a cada chat)

| Decisão | Resposta oficial |
|---------|------------------|
| Módulos localhost × nuvem são iguais? | **Sim no código.** Muda só onde roda + `.env` (+ opcionalmente provedor LLM). |
| Precisa de GPU? | **Não.** Hugging Face em CPU (Amadeus-Verbo 1.5B) ou LLM via API. GPU só acelera. |
| Onde mostrar aos amigos primeiro? | **Localhost até S5.** Nuvem/WhatsApp depois. |
| Um chat por módulo? | **Sim.** Atualizar `CONTROLE_MODULOS.md` ao terminar. |
| Quem audita tudo? | Chat **COORDENADOR** lendo `CONTROLE_MODULOS.md` + checagens §4. |
| Arquitetura híbrida | Cérebro (API+RAG) no servidor; painel Streamlit pode ficar no PC. |

---

## 2. Sequência oficial (NÃO ALTERAR A ORDEM)

```
S0  Pré-requisitos (contas/chaves)     → pode ser parcial no início
S1  SO + Python + venv                 → máquina pronta
S2  M05  LLM sem GPU                   → modelo responde
S3  M06 + M07  Ingestão + Chroma       → PDFs indexados
S4  M04 + M03  Retriever + Memória     → busca + histórico
S5  M02 + M01  Orquestrador + API      → DEMO PARA AMIGOS  ★
S6  M10 + M09  Painel + Auditoria      → controle e conformidade
S7  Domínio + HTTPS (nuvem/VPS)        → endereço público
S8  WhatsApp (Twilio ou Meta)          → mensagem real no celular
S9  Billing Asaas (opcional)           → só se for cobrar
```

### Critério de “pode avançar”

| Etapa | Só avance se… |
|-------|----------------|
| S0→S1 | `ADMIN_API_KEY` gerada (resto das contas pode esperar) |
| S1→S2 | `python3.11` + venv + `pip install -r requirements.txt` OK |
| S2→S3 | Modelo HF responde **ou** API LLM responde uma conta simples |
| S3→S4 | `python scripts/run_indexing.py` sem erro fatal; `data/chroma/` existe |
| S4→S5 | Retriever devolve chunk; memória guarda turnos |
| S5→S6 | `curl http://127.0.0.1:8000/health` OK + 1 pergunta com citação |
| S6→S7 | Demo local estável (amigos já viram) |
| S7→S8 | `https://SEU_DOMINIO/health` OK |
| S8→S9 | WhatsApp end-to-end OK (billing não bloqueia demo) |

---

## 3. Tabela mestre: etapa × módulo × pasta × chat × docs

| Etapa | Módulo(s) | Pasta(s) no projeto | Nome sugerido do chat | Docs obrigatórios no chat |
|-------|-----------|---------------------|------------------------|---------------------------|
| **S0** | — (contas) | `.env` (depois) | `deepEdu S0 pré-requisitos` | `INSTALACAO_INFRAESTRUTURA.md` §3 |
| **S1** | Infra base | sistema / venv | `deepEdu S1 ambiente` | `INSTALACAO_INFRAESTRUTURA.md` Fases 1–5 |
| **S2** | **M05** | `app/core/llm_factory.py`, `app/rag/sympy_tool.py` | `deepEdu M05 LLM` | Este + REQUISITOS RF14/RF35 + CONTROLE |
| **S3** | **M06+M07** | `app/rag/indexer.py`, `loader.py`, `data/` | `deepEdu M06-M07 ingestão` | RF15–RF24 + CONTROLE |
| **S4a** | **M04** | `app/rag/retriever.py`, `reranker.py` | `deepEdu M04 retriever` | RF13, RF26 + CONTROLE |
| **S4b** | **M03** | `app/memory/` | `deepEdu M03 memória` | RF03, RF08 + CONTROLE |
| **S5a** | **M02** | `app/services/`, `app/rag/chain.py` | `deepEdu M02 orquestrador` | RF04, RF12, RF46 + TOKEN_BUDGET |
| **S5b** | **M01** | `app/api/`, `app/integrations/` | `deepEdu M01 API` | RF05, RF40 (webhook depois) |
| **S6a** | **M10** | `control_panel/` | `deepEdu M10 painel` | RF44 + CONTROLE |
| **S6b** | **M09** | `app/audit/` | `deepEdu M09 auditoria` | RF31, RF47 + AUDITORIA_ECA |
| **S7** | Infra nuvem | Nginx, systemd, DNS | `deepEdu S7 HTTPS` | INSTALACAO Fases 13–16 |
| **S8** | WhatsApp | Twilio/Meta | `deepEdu S8 WhatsApp` | INSTALACAO §3.3 + Fase 15 |
| **S9** | Billing | `app/billing/` | `deepEdu S9 Asaas` | INSTALACAO §3.4 (opcional) |
| **Coord** | Todos | — | `deepEdu COORDENADOR` | `CONTROLE_MODULOS.md` |

---

## 4. Prompt padrão — cole em CADA chat de módulo

```
Projeto: /home/Edidio/Projects/deepEdu

DOCUMENTOS OBRIGATÓRIOS (ler antes de codificar):
1) docs/SEQUENCIA_IMPLEMENTACAO.md  ← ordem oficial; não pular etapa
2) docs/CONTROLE_MODULOS.md         ← atualizar status ao terminar
3) docs/LOCAL_VS_NUVEM.md           ← localhost primeiro
4) docs/REQUISITOS.md              ← somente RFs deste módulo

Etapa: S__
Módulo: M__
Pastas: (conforme tabela mestre)

Regras:
- Trabalhar SOMENTE este módulo / etapa
- Testar no localhost
- Ao terminar: atualizar a linha em docs/CONTROLE_MODULOS.md
- Não misturar WhatsApp/nuvem antes de S5 estar 🟢
```

---

## 5. Prompt padrão — chat COORDENADOR

```
Projeto: /home/Edidio/Projects/deepEdu
Papel: COORDENADOR

Ler:
- docs/SEQUENCIA_IMPLEMENTACAO.md
- docs/CONTROLE_MODULOS.md
- docs/LOCAL_VS_NUVEM.md

Tarefa:
1) Conferir se a ordem S0→atual foi respeitada
2) Verificar tabela de status em CONTROLE_MODULOS.md
3) Rodar checagens da §4 de CONTROLE_MODULOS.md
4) Listar pendências (código vs operação)
5) Atualizar CONTROLE_MODULOS.md §3 e §5
6) NÃO implementar módulo novo — só auditar
```

---

## 6. Fase 0 — o que anotar (resumo; detalhe no doc de infra)

| Item | Obrigatório para demo local (S5)? | Obrigatório para WhatsApp (S8)? | Doc |
|------|-----------------------------------|---------------------------------|-----|
| `ADMIN_API_KEY` | **Sim** | Sim | INSTALACAO §3.5 |
| Domínio + DNS | Não | **Sim** | INSTALACAO §3.1 |
| LangSmith | Não | Recomendado | INSTALACAO §3.2 |
| Twilio ou Meta | Não | **Sim** | INSTALACAO §3.3 |
| Asaas | Não | Não (só cobrança) | INSTALACAO §3.4 |

---

## 7. Estrutura de pastas (código = módulos)

```
deepEdu/
├── docs/
│   ├── SEQUENCIA_IMPLEMENTACAO.md   ★ este arquivo (ordem oficial)
│   ├── CONTROLE_MODULOS.md          ★ status vivo
│   ├── LOCAL_VS_NUVEM.md
│   ├── INSTALACAO_INFRAESTRUTURA.md
│   ├── REQUISITOS.md
│   └── ...
├── app/
│   ├── integrations/     M01
│   ├── services/         M02
│   ├── memory/           M03
│   ├── rag/              M04, M05(parcial), M06, M07
│   ├── core/             M05 llm_factory, config, security
│   ├── audit/            M09
│   ├── api/              M01 HTTP + admin
│   └── billing/          S9 opcional
├── control_panel/        M10
├── data/materials/       corpus
├── data/chroma/          M07 MVP
├── scripts/              indexação, ollama, produção
├── systemd/  nginx/      S7
└── IMPLEMENTACAO.md      atalho na raiz → aponta para este doc
```

---

## 8. Checklist de fechamento por “onda”

### Onda A — Demo amigos (meta amanhã+)

- [ ] S1 ambiente OK  
- [ ] S2 LLM responde  
- [ ] S3 índice OK  
- [ ] S4 retriever + memória  
- [ ] S5 health + 1 pergunta com citação  
- [ ] `CONTROLE_MODULOS.md` atualizado até S5  

### Onda B — Operação local completa

- [ ] S6 painel Streamlit  
- [ ] S6 auditoria / testes AU  
- [ ] Chat COORDENADOR passou nas checagens  

### Onda C — Nuvem + WhatsApp

- [ ] S7 HTTPS  
- [ ] S8 mensagem real  
- [ ] S9 só se necessário  

---

## 9. Histórico

| Versão | Data | Nota |
|--------|------|------|
| 1.0 | 22/07/2026 | Documento mestre criado para eliminar dúvida de sequenciamento |
