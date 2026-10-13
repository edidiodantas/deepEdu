# Plano de implantação — este PC (Deepin + Ubuntu Server)

| Campo | Valor |
|-------|-------|
| **Objetivo** | Validar a trilha auditável **aqui** antes do servidor dedicado |
| **LLM oficial** | **Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct** via **Hugging Face** (`LLM_PROVIDER=huggingface`) |
| **Data** | 07/08/2026 |
| **Ordem oficial** | `docs/SEQUENCIA_IMPLEMENTACAO.md` (S0→S9) |

---

## 0. O que é o RAG neste projeto

```
Pergunta do aluno
       │
       ▼
┌──────────────────┐
│ 1. RETRIEVAL     │  PDFs → chunks → embeddings → Chroma
└────────┬─────────┘
         │ contexto
         ▼
┌──────────────────┐
│ 2. GERAÇÃO       │  Amadeus-Verbo (PT-BR) + prompt + SymPy
└──────────────────┘
```

**Padrão do projeto (`.env.example`):**

```env
LLM_PROVIDER=huggingface
LLM_MODEL=amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct
LLM_TOKENIZER_ID=amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct
LLM_DEVICE_MAP=auto
```

Modelo no Hugging Face:  
https://huggingface.co/amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct

Ollama / Qwen2.5-Math e APIs externas ficam como **alternativas** no `.env`, não como padrão.

---

## 1. Fase A — Deepin + Amadeus-Verbo (FAÇA ISTO)

| # | Etapa | Critério |
|---|--------|----------|
| A1 | `bash scripts/bootstrap_deepin_rag.sh` | `.venv` + deps + `.env` (huggingface/Amadeus) |
| A2 | `bash scripts/install_hf_model.sh` | modelo em cache Hugging Face |
| A3 | PDFs em `data/materials/` | ≥ 1 PDF |
| A4 | `python scripts/run_indexing.py` | `data/chroma/` existe |
| A5 | `uvicorn app.api.main:app --host 127.0.0.1 --port 8000` | API no ar |
| A6 | `curl http://127.0.0.1:8000/health` | OK |
| A7 | 1 pergunta de matemática | Resposta **com citação** do material |

---

## 2. Fase B / C

- **B:** no Ubuntu Server, mesma pasta + mesma folha `IMPRIMIR_AGORA.txt`.
- **C:** servidor com GPU acelera o Amadeus-Verbo (`LLM_DEVICE_MAP=auto`).

---

## 3. Comandos rápidos

```bash
cd ~/Projects/01_deepEdu
bash scripts/bootstrap_deepin_rag.sh
bash scripts/install_hf_model.sh
```
