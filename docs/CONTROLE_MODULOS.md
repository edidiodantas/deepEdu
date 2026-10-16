# Controle de Módulos — DeepEdu

| Campo | Valor |
|-------|-------|
| **Para que serve** | Painel único para acompanhar cada módulo, pendências e checagem de código entre conversas |
| **Quem atualiza** | O agente de **cada chat de módulo** (ao terminar) + o chat **coordenador** (revisão cruzada) |
| **Ordem oficial** | Sempre seguir `docs/SEQUENCIA_IMPLEMENTACAO.md` (não pular S0→S9) |
| **Versão** | 1.0 — 22/07/2026 |

---

## 1. O que o agente pode (e não pode) fazer

| Capacidade | Sim? | Como |
|------------|------|------|
| Ler e revisar o código de um módulo | **Sim** | Abrir `app/...`, comparar com `docs/REQUISITOS.md` |
| Rodar testes / health / indexação | **Sim** | `unittest`, `curl /health`, `run_indexing.py`, `eval_rag.py` |
| Marcar pendências neste arquivo | **Sim** | Atualizar a tabela da §3 após cada chat |
| Ver o que outro chat fez | **Só se** estiver registrado aqui ou no Git | Chats separados **não** compartilham memória automaticamente |
| “Controlar” tudo sozinho sem você abrir o chat | **Não** | Você abre o chat coordenador (ou o de módulo) e pede a verificação |
| Subir sozinho na nuvem / Twilio | **Com seu pedido** | Scripts + comandos; credenciais você preenche no `.env` |

**Resumo:** sim, posso checar códigos, achar buracos e atualizar pendências — **desde que** (1) o trabalho de cada módulo fique registrado neste arquivo e (2) você abra um chat pedindo a verificação.

---

## 2. Como usar amanhã (fluxo recomendado)

### A) Chat de um módulo (ex.: M05 LLM)

Cole no início:

```
Projeto: /home/Edidio/Projects/deepEdu
Módulo: M05
Ler: docs/SEQUENCIA_IMPLEMENTACAO.md + docs/CONTROLE_MODULOS.md + docs/REQUISITOS.md (RFs deste módulo)
Ao terminar: atualize a linha deste módulo em docs/CONTROLE_MODULOS.md
Objetivo: só este módulo, localhost.
```

### B) Chat coordenador (controle geral)

Cole quando quiser “bater o martelo”:

```
Projeto: /home/Edidio/Projects/deepEdu
Papel: COORDENADOR
Ler: docs/SEQUENCIA_IMPLEMENTACAO.md, docs/CONTROLE_MODULOS.md e docs/LOCAL_VS_NUVEM.md
Tarefa:
1) Verificar status de todos os módulos na tabela
2) Rodar checagens da §4
3) Listar pendências reais (código + operação)
4) Atualizar CONTROLE_MODULOS.md
Não implementar módulos novos nesta conversa — só auditar.
```

---

## 3. Painel de status (atualizar a cada chat)

**Legenda:** `⬜ não iniciado` · `🟡 em andamento` · `🟢 ok no localhost` · `🔵 ok na nuvem` · `🔴 bloqueado`

| Ordem | Módulo | Pasta principal | Status | Teste mínimo feito? | Pendências | Última atualização |
|-------|--------|-----------------|--------|---------------------|------------|--------------------|
| S2 | **M05** Gerador LLM | `app/core/llm_factory.py`, `app/rag/sympy_tool.py` | 🟡 | [x] código Amadeus-Verbo HF · [ ] smoke no Server | Padrão: `LLM_PROVIDER=huggingface` + Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct | 13/10/2026 |
| S3 | **M06** Ingestão | `app/rag/indexer.py`, `loader.py` | ⬜ | [ ] `run_indexing.py` | — | — |
| S3 | **M07** Vetorial | `data/chroma/`, Chroma | ⬜ | [ ] pasta/índice existe | — | — |
| S4 | **M04** Retriever | `app/rag/retriever.py`, `reranker.py` | ⬜ | [ ] busca retorna chunks | — | — |
| S4 | **M03** Memória | `app/memory/` | ⬜ | [ ] follow-up usa histórico | — | — |
| S5 | **M02** Orquestrador | `app/services/`, `app/rag/chain.py` | ⬜ | [ ] resposta + citação | — | — |
| S5 | **M01** API / canais | `app/api/`, `app/integrations/` | ⬜ | [ ] `curl /health` | — | — |
| S6 | **M10** Painel | `control_panel/` | ⬜ | [ ] Streamlit abre | — | — |
| S6 | **M09** Auditoria | `app/audit/` | ⬜ | [ ] log + testes AU | — | — |
| S8 | WhatsApp | Twilio/Meta + webhook | ⬜ | [ ] msg real | depende de HTTPS | — |
| S9 | Billing | `app/billing/` | ⬜ | [ ] opcional | Asaas opcional | — |

**Infra / operação (não é módulo de código):**

| Item | Status | Nota |
|------|--------|------|
| Plano este PC (`PLANO_ESTE_PC.md`) | 🟡 | Fase A = Amadeus-Verbo (Hugging Face PT-BR) |
| `.env` local preenchido | ⬜ | bootstrap: `scripts/bootstrap_deepin_rag.sh` |
| Amadeus-Verbo HF | ⬜ | `install_hf_model.sh` — padrão oficial |
| Corpus em `data/materials/` | ⬜ | PDFs da escola |
| Domínio + HTTPS | ⬜ | só para WhatsApp / nuvem |
| LangSmith | ⬜ | recomendado, não bloqueia demo |
| Asaas | ⬜ | opcional |
| Ubuntu Server (disco 2) | ⬜ | SO instalado; **não** é o 1º alvo de teste |

---

## 4. Checagens que o coordenador deve rodar

Execute na ordem (localhost):

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate

# 1) Dependências e imports críticos
python -c "import langchain, fastapi, chromadb; from app.core.llm_factory import *; print('imports OK')"

# 2) Testes automatizados
python -m unittest discover -s tests -v

# 3) API no ar? (em outro terminal: uvicorn app.api.main:app --host 127.0.0.1 --port 8000)
curl -s http://127.0.0.1:8000/health

# 4) Índice existe?
ls -la data/chroma/ data/materials/

# 5) Avaliação RAG (quando M02–M07 estiverem 🟢)
python scripts/eval_rag.py
```

O coordenador deve anotar em **§5** o que falhou.

---

## 5. Log de verificações do coordenador

| Data | Escopo | Resultado | Ações |
|------|--------|-----------|-------|
| 28/07/2026 | M05 (S2) | Código alinhado a Qwen+Ollama (legado). | — |
| 17/09/2026 | LLM oficial | Padrão = Amadeus-Verbo HF; cache do modelo; chunks 600/120; PyMuPDF | Pendrive + push GitHub |

*(Exemplo de linha futura: `23/07 | S2–S5 | health OK, 2 testes falharam | corrigir M04 score`)*

---

## 6. Ligação com outros docs

| Doc | Uso |
|-----|-----|
| `docs/SEQUENCIA_IMPLEMENTACAO.md` | **Ordem oficial** S0→S9 (fonte da verdade) |
| `docs/LOCAL_VS_NUVEM.md` | Ordem S0–S9 e “módulos iguais?” |
| `docs/INSTALACAO_INFRAESTRUTURA.md` | Hardware + Fase 0 (contas) |
| `docs/REQUISITOS.md` | Critérios de aceite por RF |
| `docs/REVISAO_IMPLEMENTACAO.md` | Baseline histórico do código (v3.0) |
| **Este arquivo** | Status **vivo** do que você está subindo agora |

> `REVISAO_IMPLEMENTACAO.md` diz que o repositório já tinha implementação ampla. Este **Controle** serve para a **onda atual**: testar módulo a módulo no seu servidor e marcar o que está de pé de verdade no seu ambiente.

---

## 7. Resposta direta à sua pergunta

**Sim** — posso:

1. controlar o andamento pelos status deste arquivo  
2. verificar pendências quando você “subir” um módulo  
3. checar o código (e rodar testes) sob pedido  

**Como:** use chats de módulo para implementar/testar **e** um chat **COORDENADOR** (prompt da §2B) para auditar tudo junto. Sem este arquivo atualizado, cada conversa nova começa “cega” sobre o que as outras fizeram.
