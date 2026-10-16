# deepEdu

Tutor de Matemática do Ensino Médio. A pergunta da tese é se o pipeline pode ser auditado: consentimento, recuperação, geração e resposta ficam numa trilha verificável. O RAG é o objeto auditado, não o tema da pesquisa.

**LLM oficial:** [Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct](https://huggingface.co/amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct) (0,49B parâmetros, PT-BR) via Hugging Face (`LLM_PROVIDER=huggingface`). Cabe em notebook modesto; GPU só acelera.

## Comece pela implementação (ordem oficial)

| Arquivo | Função |
|---------|--------|
| **[IMPLEMENTACAO.md](IMPLEMENTACAO.md)** | Atalho na raiz |
| **[docs/SEQUENCIA_IMPLEMENTACAO.md](docs/SEQUENCIA_IMPLEMENTACAO.md)** | **Fonte da verdade** — sequência S0→S9 |
| **[IMPRIMIR_AGORA.txt](IMPRIMIR_AGORA.txt)** | Folha de instalação Ubuntu LTS (imprimir) |
| **[IMPRIMIR_COPIAR_PASTA_DEEPEDU.txt](IMPRIMIR_COPIAR_PASTA_DEEPEDU.txt)** | Como copiar a pasta (pendrive — leigo) |
| [docs/CONTROLE_MODULOS.md](docs/CONTROLE_MODULOS.md) | Status e pendências entre chats |
| [docs/LOCAL_VS_NUVEM.md](docs/LOCAL_VS_NUVEM.md) | Localhost × nuvem |
| [docs/INSTALACAO_INFRAESTRUTURA.md](docs/INSTALACAO_INFRAESTRUTURA.md) | Hardware + Ubuntu + contas (Fase 0) |
| [docs/README.md](docs/README.md) | Índice completo da documentação |

**Regra:** localhost até S5 (demo) → depois nuvem/WhatsApp. Um chat por módulo. Sem GPU obrigatória.

## Arquitetura hibrida (enxuta)

Modelo recomendado para escalar com controle simples:
- **Nuvem (grosso do sistema):** API FastAPI, RAG, billing, webhooks e banco.
- **Local (escola/operacao):** painel grafico leve para controle administrativo.

Assim voce evita manter logica pesada localmente e centraliza manutencao na nuvem.

## LLM (Amadeus-Verbo)

```bash
cd ~/Projects/01_deepEdu   # neste PC / Deepin
# no servidor Ubuntu: cd ~/deepEdu
source .venv/bin/activate
bash scripts/install_hf_model.sh
```

No `.env` (padrão do projeto):

```env
LLM_PROVIDER=huggingface
LLM_MODEL=amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct
LLM_TOKENIZER_ID=amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct
LLM_DEVICE_MAP=auto
```

## 1) Preparacao base do Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-dev python3-pip build-essential poppler-utils
```

## 2) Ambiente Python

```bash
cd ~/Projects/01_deepEdu
# no servidor: cd ~/deepEdu
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

## 3) Variaveis de ambiente

```bash
cp .env.example .env
```

Preencha no `.env` (mínimo para demo local):
- `ADMIN_API_KEY`
- `AUDIT_PHONE_SALT`
- `PHONE_ENCRYPTION_KEY`
- bloco LLM Amadeus (já vem no `.env.example`)

A pergunta do aluno entra em `POST /perguntar` ou na aba Pergunta do painel.

## 4) Materiais e indexacao

Coloque arquivos didaticos em `data/materials` (`.pdf`, `.txt`, `.md`) e rode:

```bash
source .venv/bin/activate
python scripts/run_indexing.py
```

### Limites do RAG com livros (importante)

O deepEdu indexa **texto** dos PDFs (via PyMuPDF). **Não entram no RAG:**

- figuras, diagramas, gráficos e imagens
- esquemas desenhados sem texto selecionável
- PDFs só escaneados (imagem) sem OCR

Tabelas e fórmulas em texto/Unicode costumam ser extraídas melhor com PyMuPDF; ainda assim, o aluno precisa de enunciado em texto. Se a dúvida depender só de uma figura, o tutor deve pedir reformulação ou indicar a página do livro.

Chunks (padrão atual no `.env`):

```env
CHUNK_CHILD_TOKENS=600
CHUNK_OVERLAP_TOKENS=120
```

Após mudar chunk/overlap, rode de novo `python scripts/run_indexing.py` (a coleção Chroma é reconstruída).

### Pelo painel (sem linha de comando)

Na aba **Materiais** do painel (`control_panel`): envie PDFs/TXT/MD, veja a lista, remova arquivos e clique em **Reindexar**. O tutor usa o índice novo já na próxima pergunta. Cada upload (com SHA-256), remoção e reindexação fica na trilha de auditoria (`admin.material.*`, `admin.index.rebuild`). Rotas usadas (exigem `X-Admin-Api-Key`): `GET/POST /admin/materials`, `DELETE /admin/materials/{arquivo}`, `POST /admin/index/rebuild`.

## 5) Teste local da API

```bash
source .venv/bin/activate
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## 6) Deploy de producao (systemd + Nginx + HTTPS)

### Opcao automatica (recomendada)

O script abaixo instala Nginx/Certbot, sobe o servico, cria virtual host e emite TLS:

```bash
chmod +x scripts/setup_production.sh
./scripts/setup_production.sh SEU_DOMINIO SEU_USUARIO
```

Exemplo:

```bash
./scripts/setup_production.sh tutor.escola.com edidio
```

### Opcao manual

1. Ajuste `systemd/deepedu.service` trocando `SEU_USUARIO`.
2. Instale o servico:

```bash
sudo cp systemd/deepedu.service /etc/systemd/system/deepedu.service
sudo systemctl daemon-reload
sudo systemctl enable deepedu
sudo systemctl start deepedu
```

3. Crie o vhost Nginx usando `nginx/deepedu.conf.template`.
4. Emita certificado:

```bash
sudo certbot --nginx -d SEU_DOMINIO
```

## 7) Pergunta local

Com a API no ar em `http://127.0.0.1:8000`:

```bash
curl -s http://127.0.0.1:8000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"student_id":"aluno-local","question":"quanto e 2+2?"}'
```

A resposta inclui `correlation_id`. Os eventos dessa pergunta ficam em `data/audit/audit.db`. O painel Streamlit, aba Pergunta, faz a mesma chamada.

## 8) Operacao e observabilidade

```bash
sudo systemctl status deepedu
sudo systemctl status nginx
journalctl -u deepedu -f
```

## Painel grafico local (controle)

Foi adicionado um painel local com Streamlit em `control_panel/`.
Ele conversa com a API em nuvem via endpoints internos protegidos por `ADMIN_API_KEY`.

### 1) Configurar painel local

```bash
cd control_panel
cp .env.example .env
```

Edite `.env`:
- `CLOUD_API_BASE_URL=https://SEU_DOMINIO`
- `ADMIN_API_KEY` (mesma chave do servidor)

### 2) Instalar e executar painel

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-control.txt
streamlit run streamlit_app.py
```

### 3) Funcoes atuais no painel
- ativar assinatura individual
- gerar checkout individual
- criar escola
- vincular aluno em escola
- gerar checkout de plano escola
- ativar plano escola manualmente (teste)

## Monetizacao (base ja preparada)

O projeto ja possui base de assinatura por telefone:
- tabela local em SQLite (`data/billing/billing.db`)
- criacao automatica de aluno novo com status `trial`
- bloqueio opcional no webhook por assinatura

Para ativar o bloqueio:
1. Ajuste no `.env`: `BILLING_ENFORCE_SUBSCRIPTION=true`
2. Reinicie o servico:

```bash
sudo systemctl restart deepedu
```

Endpoint interno para ativar assinatura em testes:

```bash
curl -X POST "http://127.0.0.1:8000/admin/billing/activate?phone=%2B5511999999999" -H "X-Admin-Api-Key: SUA_CHAVE"
```

## Integracao com gateway brasileiro (Asaas)

Ja integrada no codigo:
- criacao de cliente e cobranca PIX
- webhook para ativacao automatica de assinatura

### 1) Configurar `.env`

Preencha:
- `ASAAS_API_KEY`
- `ASAAS_WEBHOOK_TOKEN`
- `ASAAS_BILLING_AMOUNT`
- `PUBLIC_BASE_URL`

### 2) Criar checkout (link de pagamento)

```bash
curl -X POST "http://127.0.0.1:8000/admin/billing/checkout?phone=%2B5511999999999&name=Aluno%20Teste" -H "X-Admin-Api-Key: SUA_CHAVE"
```

Resposta inclui `invoice_url` para enviar ao aluno.
Voce pode escolher metodo:
- `billing_type=PIX`
- `billing_type=BOLETO`
- `billing_type=CREDIT_CARD`
- `billing_type=UNDEFINED` (recomendado: permite opcoes no checkout)

Exemplo com cartao:

```bash
curl -X POST "http://127.0.0.1:8000/admin/billing/checkout?phone=%2B5511999999999&name=Aluno%20Teste&billing_type=CREDIT_CARD" -H "X-Admin-Api-Key: SUA_CHAVE"
```

### 3) Configurar webhook no painel Asaas

URL:
`https://SEU_DOMINIO/webhook/asaas`

Header/token:
- configure no painel um token e use o mesmo valor em `ASAAS_WEBHOOK_TOKEN`.

### 4) Eventos tratados

- `PAYMENT_CONFIRMED` / `PAYMENT_RECEIVED` -> assinatura `active`
- `PAYMENT_OVERDUE` / `PAYMENT_DELETED` -> `past_due`
- `PAYMENT_REFUNDED` / `PAYMENT_CHARGEBACK_REQUESTED` -> `canceled`

### 5) Link automatico no WhatsApp quando bloqueado

Quando `BILLING_ENFORCE_SUBSCRIPTION=true` e o aluno estiver sem acesso, o bot tenta gerar automaticamente
um checkout e envia no WhatsApp um link com opcoes de pagamento (PIX, boleto e cartao).

### 6) Autoatendimento no WhatsApp (sem suporte manual)

Comandos que o aluno pode enviar:
- `ajuda` -> mostra menu de autoatendimento
- `pagar` -> gera link com opcoes (PIX, boleto, cartao)
- `pagar pix` -> gera checkout focado em PIX
- `pagar boleto` -> gera checkout focado em boleto
- `pagar cartao` -> gera checkout focado em cartao
- `status` -> informa status e, se necessario, reenvia link

Se o aluno estiver bloqueado e enviar qualquer duvida de materia, o sistema responde com link de pagamento automaticamente.

### 7) Fluxo para professores via WhatsApp

Configure no `.env` os numeros autorizados:
- `PROFESSOR_WHATSAPP_NUMBERS=+5511999990001,+5511999990002`

Comandos do professor:
- `professor ajuda`
- `professor status` (resumo de assinaturas)
- `professor aviso <mensagem>` (dispara aviso para alunos `active` e `trial`)

Exemplo:
- `professor aviso Revisao de fisica hoje as 19h.`

## Plano Escola (B2B) - base implementada

Agora o sistema suporta 2 modelos em paralelo:
- aluno individual
- escola com plano fixo para alunos vinculados

Regra de acesso:
- se aluno estiver vinculado a escola com plano `active`, acesso liberado
- caso contrario, cai no fluxo individual (trial/assinatura)

### Config no `.env`

- `SCHOOL_PLAN_AMOUNT` (valor fixo da escola)
- `SCHOOL_PLAN_DAYS` (dias de vigencia por pagamento)

### Endpoints internos de gestao escola

1) Criar escola:

```bash
curl -X POST "http://127.0.0.1:8000/admin/schools?school_id=escola-alpha&name=Escola%20Alpha" -H "X-Admin-Api-Key: SUA_CHAVE"
```

2) Vincular aluno:

```bash
curl -X POST "http://127.0.0.1:8000/admin/schools/assign-student?phone=%2B5511999999999&school_id=escola-alpha" -H "X-Admin-Api-Key: SUA_CHAVE"
```

3) Gerar checkout da escola (Asaas):

```bash
curl -X POST "http://127.0.0.1:8000/admin/schools/checkout?school_id=escola-alpha&school_name=Escola%20Alpha" -H "X-Admin-Api-Key: SUA_CHAVE"
```

4) Ativacao manual (teste):

```bash
curl -X POST "http://127.0.0.1:8000/admin/schools/activate?school_id=escola-alpha" -H "X-Admin-Api-Key: SUA_CHAVE"
```

### Webhook Asaas escola

No pagamento da escola, o `externalReference` e enviado como `school:<school_id>`.
Quando o webhook receber:
- `PAYMENT_CONFIRMED`/`PAYMENT_RECEIVED` -> plano escola `active`
- `PAYMENT_OVERDUE`/`PAYMENT_DELETED` -> `past_due`
- `PAYMENT_REFUNDED`/`PAYMENT_CHARGEBACK_REQUESTED` -> `canceled`

## 9) Checklist de validacao fim a fim

### A. DNS e rede
- O dominio aponta para o IP publico do servidor (`A` record).
- Portas liberadas no firewall/security group: `80/tcp` e `443/tcp`.
- No servidor, confirme:

```bash
sudo ufw status
sudo ss -ltnp | rg ":80 |:443 |:8000 "
```

### B. Aplicacao
- Ambiente virtual ativo e dependencias instaladas.
- Indexacao executada sem erro (`python scripts/run_indexing.py`).
- Health local responde:

```bash
curl http://127.0.0.1:8000/health
```

### C. Servicos
- `deepedu` ativo e habilitado no boot.
- `nginx` ativo.

```bash
sudo systemctl is-enabled deepedu
sudo systemctl is-active deepedu
sudo systemctl is-active nginx
```

### D. TLS
- Certificado emitido para o dominio correto.
- URL publica responde HTTPS sem erro:

```bash
curl -I https://SEU_DOMINIO/health
```

### E. Pergunta local
- `POST /perguntar` responde e devolve `correlation_id`.
- O mesmo id aparece em `data/audit/audit.db`.

### F. Teste real
- Envie uma pergunta pelo painel ou pelo curl de `/perguntar`.
- Confira a resposta e os logs:

```bash
journalctl -u deepedu -f
```

## 10) Validacao automatizada (script)

Execute:

```bash
chmod +x scripts/validate_production.sh
./scripts/validate_production.sh SEU_DOMINIO
```

Esse script verifica:
- comandos basicos do sistema
- status `deepedu` e `nginx`
- portas 8000/80/443
- DNS do dominio
- certificado TLS
- health local e publico
- logs recentes dos servicos

## 11) Benchmark DeepSeek vs Phi (comparacao)

Com os dois projetos lado a lado (`deepEdu` e `deepedu_phi_compare`), rode:

```bash
python scripts/benchmark_architectures.py --runs 2 --warmup 1
```

Saidas:
- `data/benchmarks/benchmark_<timestamp>.json`
- `data/benchmarks/benchmark_<timestamp>.md`

## Estrutura dos modulos

- `app/rag/indexer.py`: carrega e indexa materiais
- `app/rag/retriever.py`: busca hibrida (BM25 + vetorial Chroma)
- `app/memory/history.py`: historico por telefone em SQLite
- `app/services/tutor_service.py`: orquestra resposta do tutor
- `app/api/main.py`: API local (`/health`, `/perguntar`, admin)
