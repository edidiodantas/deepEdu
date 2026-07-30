# Orçamento de Tokens — Qwen2.5-Math-1.5B-Instruct

| Campo | Valor |
|-------|-------|
| **Modelo** | `Qwen2.5-Math-1.5B-Instruct` |
| **Janela de contexto** | **4.096 tokens** (`max_position_embeddings`) |
| **Tokenizer** | `Qwen/Qwen2.5-Math-1.5B-Instruct` (via `transformers` ou `tiktoken` compatível) |
| **Versão** | 1.0 |
| **Data** | 29/06/2026 |

> **Importante:** A série **Qwen2.5-Math** usa janela de **4K**, não os 128K do Qwen2.5 genérico. Forçar contexto maior (`VLLM_ALLOW_LONG_MAX_MODEL_LEN`) **não é recomendado** — causa saídas incorretas ou erros CUDA.

---

## 1. Distribuição do orçamento (padrão produção)

| Componente | Máximo (tokens) | Variável de config | Observação |
|------------|:---------------:|-------------------|------------|
| Prompt de sistema | 400 | `PROMPT_MAX_TOKENS` | Ver `prompts/v1_tutor_em.md` (~250–350 na prática) |
| Contexto RAG (total) | 1.200 | `RAG_CONTEXT_MAX_TOKENS` | Soma de todos os chunks injetados |
| Histórico de chat | 800 | `HISTORY_MAX_TOKENS` | Buffer + resumo (RF08) |
| Mensagem do usuário | 400 | `USER_MESSAGE_MAX_TOKENS` | Truncar se exceder; pedir reformulação |
| Overhead (tags, formatação) | 100 | — | Marcadores `<context>`, etc. |
| **Subtotal de entrada** | **~2.900** | | |
| **Geração (`max_new_tokens`)** | **1.024** | `LLM_MAX_NEW_TOKENS` | Resposta do tutor |
| **Total estimado** | **~3.924** | | Margem de segurança: ~172 tokens |

---

## 2. Regras de truncagem (ordem de prioridade)

Quando a entrada exceder o limite, aplicar **nesta ordem**:

1. **Truncar chunks RAG** — reduzir de `top_k=3` para `top_k=2`, depois `top_k=1`
2. **Resumir histórico** — acionar resumo automático (RF08) mantendo tema e dados do problema
3. **Truncar chunks individualmente** — cada chunk a no máximo 400 tokens (corte por fim de parágrafo)
4. **Truncar mensagem do usuário** — apenas se > 400 tokens; avisar o usuário
5. **Nunca truncar** o prompt de sistema abaixo de 200 tokens (persona + regras críticas)

Se ainda exceder após truncagem: **abstinência** (RF37) com mensagem pedindo pergunta mais curta.

---

## 3. Parâmetros RAG alinhados ao orçamento

| Parâmetro | Valor padrão | Justificativa |
|-----------|:------------:|---------------|
| `RETRIEVAL_TOP_K` | 3 | 3 × 400 tokens = 1.200 tokens de contexto |
| `CHUNK_CHILD_TOKENS` | 300–400 | Busca granular sem estourar janela |
| `CHUNK_PARENT_MAX_TOKENS` | 400 | **Corrigido** — não 1.500 (incompatível com 4K) |
| `LLM_MAX_NEW_TOKENS` | 1.024 | Respostas pedagógicas com passos |
| `LLM_TEMPERATURE` | 0.3 | Menor variância em matemática |
| `HISTORY_BUFFER_MESSAGES` | 4 | Últimas 4 trocas antes de resumir |
| `HISTORY_SUMMARY_TRIGGER` | 600 tokens | Dispara resumo do histórico |

---

## 4. Contagem de tokens

**Obrigatório:** usar o tokenizer do próprio modelo Qwen para contagem — **não** estimar por caracteres.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Math-1.5B-Instruct")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))
```

Registrar no LangSmith (RF31): `input_tokens`, `rag_tokens`, `history_tokens`, `output_tokens`.

---

## 5. Limites por canal

### WhatsApp
- Mensagem típica do aluno: 50–150 tokens
- Resposta alvo: 200–600 tokens (evitar textos longos; usar passos numerados curtos)
- Se resposta > 800 tokens: dividir em 2 mensagens sequenciais

### Dashboard web
- Mesmos limites de entrada
- Pode exibir resposta completa até `max_new_tokens`

---

## 6. Template de montagem do prompt

```
[System — máx. 400 tokens]
{prompts/v1_tutor_em.md}

[Contexto RAG — máx. 1.200 tokens]
<context>
{chunk_1}
---
{chunk_2}
---
{chunk_3}
</context>

[Histórico — máx. 800 tokens]
{history_summary_or_buffer}

[Usuário — máx. 400 tokens]
{user_message}
```

---

## 7. Testes de aceitação

| ID | Teste | Critério |
|----|-------|----------|
| TB-01 | Prompt sistema | ≤ 400 tokens |
| TB-02 | 3 chunks + histórico médio + pergunta | Entrada ≤ 2.900 tokens |
| TB-03 | Pergunta com 10 turnos de conversa | Resumo ativado; sem erro de contexto |
| TB-04 | Pergunta de 2.000 caracteres | Truncada ou recusa educada |
| TB-05 | LangSmith trace | Campos de token preenchidos |

---

## 8. Referência técnica

- `config.json` do modelo: `max_position_embeddings: 4096`
- [Qwen2.5-Math Technical Report](https://arxiv.org/html/2409.12122v1) — treino com context length 4K
- [Hugging Face — Qwen2.5-Math-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Math-1.5B-Instruct)
