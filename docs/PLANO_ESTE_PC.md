# Plano de implantação — este PC (Deepin + Ubuntu Server)

| Campo | Valor |
|-------|-------|
| **Objetivo** | Validar o **RAG** deepEdu **aqui** antes do servidor dedicado com GPU |
| **LLM oficial** | **Qwen2.5-Math** via **Ollama** (`LLM_PROVIDER=ollama`) — **não** DeepSeek |
| **Data** | 23/07/2026 |
| **Ordem oficial** | `docs/SEQUENCIA_IMPLEMENTACAO.md` (S0→S9) |

---

## 0. O que é o RAG neste projeto (para não confundir)

O deepEdu **não** é “só um chat com Qwen”. É um **RAG**:

```
Pergunta do aluno
       │
       ▼
┌──────────────────┐
│ 1. RETRIEVAL     │  PDFs em data/materials/ → pedaços (chunks)
│    (busca)       │  → embeddings → Chroma → trechos relevantes
└────────┬─────────┘
         │ contexto (citações do material)
         ▼
┌──────────────────┐
│ 2. GERAÇÃO       │  Qwen2.5-Math (Ollama) + prompt + SymPy
│    (LLM)         │  → resposta com base no material
└──────────────────┘
```

| Peça | O que faz | Onde roda (Fase A) |
|------|-----------|---------------------|
| PDFs / corpus | Material didático | `data/materials/` |
| Indexação (M06) | Quebra PDF e grava no banco vetorial | Deepin, `run_indexing.py` |
| Chroma (M07) | Guarda vetores | `data/chroma/` |
| Retriever (M04) | Acha trechos certos | Código Python local |
| **Qwen2.5-Math (M05)** | Escreve a resposta usando o contexto | **Ollama local** |
| API FastAPI | Junta tudo e expõe HTTP | `uvicorn` no Deepin |

Sem indexação + Chroma, **não é RAG** — seria só o Qwen “do zero”.  
Sem Qwen, a busca existe mas **não gera** a resposta tutora.

**Padrão do projeto (`.env.example`):**

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-math:1.5b-instruct
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

DeepSeek era só uma alternativa opcional de API. **Você não usa.** Esquecemos isso neste plano.

---

## 1. Três fases (mesmo PC → servidor GPU)

```
FASE A — AGORA                    FASE B — opcional              FASE C — destino
─────────────────────────────     ─────────────────────          ────────────────────
Deepin (disco 1)                  Ubuntu Server (disco 2)        Servidor com GPU
RAG completo + Ollama + Qwen      Repetir o mesmo RAG            Mesmo RAG, mais rápido
Teste: curl /health + 1 pergunta  (sem GUI, só terminal)         + HTTPS + WhatsApp
```

| Disco | Agora | Depois |
|-------|--------|--------|
| **Deepin** | Onde **sobe e testa o RAG** | Docs, Cursor, painel Streamlit |
| **Ubuntu Server** | SO limpo — **ainda não** | Ensaio “tipo servidor” se quiser |
| **Servidor + GPU** | Não | Produção com o **mesmo** Qwen/Ollama |

Em dual boot, Deepin e Ubuntu **não rodam juntos**. Por isso o 1º teste do RAG é **tudo no Deepin**.

---

## 2. Fase A — Deepin + Ollama + Qwen (FAÇA ISTO)

Objetivo: RAG de ponta a ponta até **S5**.

| # | Etapa | Critério |
|---|--------|----------|
| A1 | `bash scripts/bootstrap_deepin_rag.sh` | `.venv` + deps + `.env` (ollama/Qwen) |
| A2 | `bash scripts/install_ollama_model.sh` | `ollama list` mostra `qwen2.5-math` |
| A3 | PDFs em `data/materials/` | ≥ 1 PDF |
| A4 | `python scripts/run_indexing.py` | `data/chroma/` existe (**retrieval**) |
| A5 | `uvicorn app.api.main:app --host 127.0.0.1 --port 8000` | API no ar |
| A6 | `curl http://127.0.0.1:8000/health` | OK |
| A7 | 1 pergunta de matemática | Resposta **com citação** do material |

Isso prova o **RAG** (busca + Qwen), não só o modelo.

---

## 3. Fase B / C (resumo)

- **B:** no Ubuntu do disco 2, repetir A1–A6 (mesmo código, Ollama + Qwen).
- **C:** no servidor com GPU, mesmo `.env` ollama; depois Nginx/WhatsApp (`INSTALACAO_INFRAESTRUTURA.md`).

---

## 4. Comandos (Deepin)

```bash
cd ~/Projects/deepEdu
bash scripts/bootstrap_deepin_rag.sh
bash scripts/install_ollama_model.sh

# PDFs → data/materials/
source .venv/bin/activate
python scripts/run_indexing.py
uvicorn app.api.main:app --host 127.0.0.1 --port 8000
# outro terminal:
curl http://127.0.0.1:8000/health
```

Status vivo: `docs/CONTROLE_MODULOS.md`.
