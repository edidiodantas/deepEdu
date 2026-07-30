# deepEdu — Comece aqui (implementação)

Este arquivo na **raiz do projeto** existe para não haver dúvida de por onde seguir.

## Fonte da verdade (ordem oficial)

→ **[`docs/SEQUENCIA_IMPLEMENTACAO.md`](docs/SEQUENCIA_IMPLEMENTACAO.md)**

Lá está:

- sequência **S0 → S9** (não pular)
- tabela etapa × módulo × pasta × chat
- prompts para colar em cada conversa
- o que é obrigatório para demo local vs WhatsApp

## Documentos irmãos (mesmo pacote)

| Arquivo | Função |
|---------|--------|
| [`docs/SEQUENCIA_IMPLEMENTACAO.md`](docs/SEQUENCIA_IMPLEMENTACAO.md) | **Ordem oficial** |
| [`docs/CONTROLE_MODULOS.md`](docs/CONTROLE_MODULOS.md) | Status / pendências / coordenador |
| [`docs/LOCAL_VS_NUVEM.md`](docs/LOCAL_VS_NUVEM.md) | Localhost = nuvem no código? |
| [`docs/INSTALACAO_INFRAESTRUTURA.md`](docs/INSTALACAO_INFRAESTRUTURA.md) | Hardware + Ubuntu + Fase 0 (contas) |
| [`docs/REQUISITOS.md`](docs/REQUISITOS.md) | RF/RNF por módulo |
| [`docs/README.md`](docs/README.md) | Índice de toda a documentação |

## Regra de ouro

1. Localhost até **S5** (demo).  
2. Um chat por módulo.  
3. Atualizar `CONTROLE_MODULOS.md` ao terminar.  
4. Nuvem/WhatsApp só depois.  
5. Sem GPU obrigatória.

## Neste PC (Deepin + Ubuntu no disco 2)

→ **[`docs/PLANO_ESTE_PC.md`](docs/PLANO_ESTE_PC.md)** — RAG no Deepin com **Ollama + Qwen2.5-Math**; Ubuntu Server e GPU só depois.

```bash
cd ~/Projects/deepEdu
bash scripts/bootstrap_deepin_rag.sh
bash scripts/install_ollama_model.sh
```
