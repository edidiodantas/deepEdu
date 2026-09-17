# Localhost × Nuvem — deepEdu

| Campo | Valor |
|-------|-------|
| **Pergunta** | Os módulos na nuvem e no localhost são iguais? |
| **Resposta curta** | **Sim — o código dos módulos é o mesmo.** O que muda é *onde* roda, o `.env` e (opcionalmente) o provedor de LLM. |
| **Sem GPU?** | Sim. Use Amadeus-Verbo em CPU (Hugging Face) **ou** LLM via API. GPU só acelera; não é obrigatória. |
| **Versão** | 1.0 — 22/07/2026 |

---

## 1. Resposta clara (para não ter medo)

Imagine o deepEdu como um **mesmo programa** que você pode ligar em dois lugares:

| | **Localhost (sua máquina / servidor local)** | **Nuvem (VPS sem GPU)** |
|--|---------------------------------------------|-------------------------|
| Código | `app/`, `control_panel/`, `scripts/` | **Mesmo** repositório |
| Módulos M01–M10 | **Iguais** | **Iguais** |
| O que muda | `ENV=development`, URL `http://127.0.0.1:8000` | `ENV=production`, domínio HTTPS, systemd/Nginx |
| WhatsApp | Só funciona de verdade com túnel (ngrok) **ou** depois na nuvem | Webhook oficial `https://seu-dominio/...` |
| Objetivo agora | Mostrar para os amigos **já** | Repetir o que já funciona, só “mudando o endereço” |

**Regra de ouro:** faça funcionar no localhost primeiro. Subir na nuvem depois é quase “copiar a pasta + ajustar `.env` + Nginx”. Não é outro projeto.

---

## 2. Dois sentidos da palavra “módulo” (não confundir)

### A) Módulos de **negócio** (código — iguais em todo lugar)

Definidos em `docs/REQUISITOS.md`. Vivem sob `app/` (e o painel em `control_panel/`).

| ID | Nome | Pasta no projeto | Roda no localhost? | Roda na nuvem? |
|----|------|------------------|--------------------|----------------|
| **M01** | Canais (WhatsApp / web) | `app/integrations/`, `app/api/` | Sim (teste local; WhatsApp real precisa HTTPS) | Sim |
| **M02** | Orquestrador RAG | `app/services/`, `app/rag/chain.py` | Sim | Sim |
| **M03** | Memória de conversa | `app/memory/` | Sim | Sim |
| **M04** | Retriever híbrido | `app/rag/retriever.py`, `reranker.py` | Sim | Sim |
| **M05** | Gerador (LLM + SymPy) | `app/core/llm_factory.py`, `app/rag/sympy_tool.py` | Sim | Sim |
| **M06** | Ingestão / indexação | `app/rag/indexer.py`, `loader.py`, `scripts/run_indexing.py` | Sim | Sim |
| **M07** | Banco vetorial | Chroma em `data/chroma/` (MVP) | Sim | Sim (mesmo código; depois Qdrant se quiser) |
| **M08** | Metadados BNCC | (evolução; metadados nos chunks) | Sim | Sim |
| **M09** | Governança / auditoria | `app/audit/`, LangSmith | Sim (LangSmith opcional) | Sim (recomendado) |
| **M10** | Dashboard | `control_panel/` (Streamlit) | Sim (PC local) | **Opcional** — pode continuar no PC da escola |

### B) Módulos de **implantação** (onde cada peça “mora”)

Aqui localhost e nuvem **não** são idênticos na *topologia* — e isso é de propósito (arquitetura híbrida do README):

```
┌─────────────────────────────────────────────────────────┐
│  NUVEM / SERVIDOR (o “cérebro”)                         │
│  M01 webhooks · M02–M07 RAG · M09 auditoria · billing   │
│  FastAPI :8000 · Ollama ou API LLM · Chroma · Nginx     │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ HTTPS + ADMIN_API_KEY
                          │
┌─────────────────────────────────────────────────────────┐
│  LOCALHOST / PC DA ESCOLA (só o “controle remoto”)      │
│  M10 painel Streamlit → chama a API na nuvem            │
└─────────────────────────────────────────────────────────┘
```

**No começo (só mostrar aos amigos):** você pode rodar **tudo no localhost** — cérebro + painel na mesma máquina. Depois, quando for para a nuvem, **move o cérebro**; o painel pode continuar no PC.

---

## 3. Sequência de implantação (explícita — não pule)

Faça **nesta ordem**. Cada etapa tem pasta/documento de apoio.

| Ordem | Etapa | Onde | Critério “pronto para amigos” | Doc / pasta |
|-------|--------|------|-------------------------------|-------------|
| **S0** | Pré-requisitos (chaves) | Fora do servidor | `ADMIN_API_KEY` gerada; resto pode esperar | `docs/INSTALACAO_INFRAESTRUTURA.md` §3 |
| **S1** | SO + Python + venv | Localhost | `pip install -r requirements.txt` OK | `docs/INSTALACAO_INFRAESTRUTURA.md` Fases 1–5 |
| **S2** | LLM **sem GPU** | Localhost | Hugging Face Amadeus-Verbo **ou** API no `.env` | `scripts/install_hf_model.sh` / `.env.example` |
| **S3** | M06 + M07 — indexar PDFs | Localhost | `python scripts/run_indexing.py` | `data/materials/`, `app/rag/` |
| **S4** | M02–M05 — API responde | Localhost | `curl http://127.0.0.1:8000/health` | `app/api/`, `app/services/` |
| **S5** | Demo para amigos | Localhost | Chat/API local respondendo matemática com citação | — |
| **S6** | M10 — painel (opcional) | Localhost | Streamlit abre e fala com a API | `control_panel/` |
| **S7** | Domínio + HTTPS | Nuvem | `https://SEU_DOMINIO/health` | Fase 13 infra |
| **S8** | M01 — WhatsApp | Nuvem | Mensagem real no celular | Twilio/Meta + webhook |
| **S9** | Billing (opcional) | Nuvem | Asaas só se for cobrar | `app/billing/` |

> **Para os amigos verem logo:** pare em **S5**. Nuvem e WhatsApp vêm depois, sem reescrever módulos.

---

## 4. Sem placa de vídeo — o que usar

| Opção | Como | Prós | Contras |
|-------|------|------|---------|
| **A — Hugging Face CPU/GPU** (padrão do projeto) | `LLM_PROVIDER=huggingface` + Amadeus-Verbo 1.5B PT-BR | 100% local, português BR, sem chave de LLM | CPU mais lento; 1º download ~2–4 GB |
| **B — API na nuvem** (sem GPU / pouca RAM) | `LLM_PROVIDER=openai_compatible` + DeepSeek (ou similar) | VPS barata; LLM “fora” | Precisa de API key e internet |
| **C — Ollama (legado)** | `LLM_PROVIDER=ollama` + Qwen2.5-Math | Alternativa antiga | Não é mais o padrão |

As duas usam o **mesmo** módulo M05 (`app/core/llm_factory.py`). Só muda o `.env`.

---

## 5. Checklist mental “não tenho medo da nuvem”

1. No localhost: `curl /health` → OK e uma pergunta de matemática responde.  
2. Na VPS: mesmo `git clone` / mesma pasta `Projects/deepEdu`.  
3. Mesmo `.venv` + `requirements.txt`.  
4. `.env` com `PUBLIC_BASE_URL=https://...` e `ENV=production`.  
5. `./scripts/setup_production.sh SEU_DOMINIO SEU_USUARIO`.  
6. Só então Twilio/WhatsApp.

Você **não** aprende “nuvem do zero” — você **repete** o que já validou em casa.

---

## 6. Pastas especiais (mapa para implantar módulo a módulo)

Use esta tabela como índice. A codificação futura de cada módulo pode seguir esta ordem (S3→S8).

```
deepEdu/
├── docs/
│   ├── LOCAL_VS_NUVEM.md          ← este arquivo (local = nuvem?)
│   ├── INSTALACAO_INFRAESTRUTURA.md
│   └── REQUISITOS.md              ← definição M01–M10
├── app/
│   ├── integrations/              ← M01 canais
│   ├── services/ + rag/chain.py   ← M02 orquestrador
│   ├── memory/                    ← M03
│   ├── rag/retriever.py           ← M04
│   ├── core/llm_factory.py        ← M05
│   ├── rag/indexer.py, loader.py  ← M06
│   ├── (data/chroma via config)   ← M07
│   ├── audit/                     ← M09
│   ├── api/                       ← HTTP (M01 + admin)
│   └── billing/                   ← opcional (Asaas)
├── control_panel/                 ← M10 (fica no PC se quiser)
├── data/materials/                ← corpus
└── scripts/                       ← indexação, produção, ollama
```

---

## 7. Próximo passo recomendado (agora)

1. Confirmar localhost em **S4/S5** (health + uma pergunta).  
2. Mostrar aos amigos.  
3. Só depois abrir um agente “nuvem” com este doc + `INSTALACAO_INFRAESTRUTURA.md` Fases 13–15.

**Controle entre chats:** use `docs/CONTROLE_MODULOS.md` — cada conversa de módulo atualiza o status; um chat **COORDENADOR** verifica pendências e roda as checagens.

**Ordem oficial (fonte da verdade):** `docs/SEQUENCIA_IMPLEMENTACAO.md` (atalho na raiz: `IMPLEMENTACAO.md`).

Se quiser, no próximo chat: “estamos na etapa Sx — faça só o módulo My”.
