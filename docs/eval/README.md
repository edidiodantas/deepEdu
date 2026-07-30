# Dataset de Avaliação RAG — Matemática Ensino Médio

## Objetivo

Conjunto de perguntas de referência para medir qualidade do RAG (RF38), executado via `scripts/eval_rag.py`.

## Arquivo

- **CSV:** `docs/eval/dataset_rag_matematica_em.csv`
- **Mínimo para produção:** 50 perguntas ativas (`ativo=true`)
- **Atual:** **50 perguntas ativas** (EM-001 a EM-050)

## Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | string | Identificador único (ex.: EM-001) |
| `pergunta` | string | Pergunta do estudante |
| `serie` | int | 1, 2 ou 3 (ano do EM) |
| `tema` | string | Tema matemático |
| `habilidade_bncc` | string | Código EM13MATxxx |
| `resposta_esperada` | string | Resposta ideal para comparação |
| `fonte_esperada` | string | Nome da fonte citada |
| `documento_esperado` | string | Arquivo no corpus |
| `pagina_esperada` | int | Página no documento |
| `requer_calculo` | bool | Se deve usar SymPy (RF35) |
| `requer_citacao` | bool | Se resposta deve citar fonte (RF29) |
| `dificuldade` | string | fácil, média, difícil |
| `ativo` | bool | Incluir na avaliação |
| `observacoes` | string | Notas para avaliadores |

## Métricas alvo

| Métrica | Limiar mínimo (F2) | Limiar produção (F3) |
|---------|:------------------:|:--------------------:|
| precision@5 | ≥ 0.60 | ≥ 0.70 |
| faithfulness | ≥ 0.70 | ≥ 0.80 |
| citation_accuracy | ≥ 0.65 | ≥ 0.75 |
| abstention_precision | ≥ 0.80 | ≥ 0.85 |

## Uso

```bash
python scripts/eval_rag.py --dataset docs/eval/dataset_rag_matematica_em.csv --output reports/eval_latest.json
```

Regressão > 5% em qualquer métrica bloqueia deploy (RNF15).
