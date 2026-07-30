# Instalação de Infraestrutura — deepEdu


| Campo                      | Valor                                                             |
| -------------------------- | ----------------------------------------------------------------- |
| **Projeto**                | deepEdu — Tutor RAG de Matemática (Ensino Médio)                  |
| **Versão**                 | 1.1                                                               |
| **Data**                   | 22/07/2026                                                        |
| **SO alvo**                | Ubuntu Server **22.04 LTS** ou **24.04 LTS**                      |
| **Escopo deste documento** | Hardware + instalação de software **antes** da codificação RAG    |
| **Próximo passo**          | Novo agente Cursor para implementação/codificação do pipeline RAG |
| **Ordem oficial do projeto** | Ver `docs/SEQUENCIA_IMPLEMENTACAO.md` (atalho: `IMPLEMENTACAO.md`) |


---

## 1. Ordem de implementação (visão geral)

Siga **exatamente esta sequência**. Cada fase depende da anterior.


| #   | Fase                 | O que instala                         | Critério de pronto                |
| --- | -------------------- | ------------------------------------- | --------------------------------- |
| 0   | Pré-requisitos       | Conta de domínio, chaves de API       | DNS e credenciais anotadas        |
| 1   | SO                   | Ubuntu Server LTS                     | Login SSH funcional               |
| 2   | Sistema base         | Atualização, usuário, firewall, SSH   | `ufw` ativo, portas 22/80/443     |
| 3   | Ferramentas de build | Git, Python 3.11+, compiladores       | `python3.11 --version` OK         |
| 4   | Projeto              | Clone do repositório deepEdu          | Pasta `~/Projects/deepEdu` existe |
| 5   | Ambiente Python      | venv + `requirements.txt`             | `pip list` mostra langchain       |
| 6   | LLM local            | Ollama + Qwen2.5-Math-1.5B            | `ollama run` responde             |
| 7   | Embeddings           | Modelo sentence-transformers (1º uso) | Download concluído em cache       |
| 8   | Configuração         | Arquivo `.env`                        | Variáveis críticas preenchidas    |
| 9   | LangSmith            | Conta + API key                       | Tracing ativo (opcional em dev)   |
| 10  | Banco vetorial       | Chroma (MVP)                          | Diretório `data/chroma/` criado   |
| 11  | Corpus               | PDFs em `data/materials/`             | Arquivos didáticos no servidor    |
| 12  | API FastAPI          | Teste manual com uvicorn              | `curl /health` → 200              |
| 13  | Produção             | systemd + Nginx + TLS                 | HTTPS público ativo               |
| 14  | Painel web           | Streamlit (controle local)            | Painel abre no navegador          |
| 15  | WhatsApp             | Twilio ou Meta Cloud API              | Webhook verificado                |
| 16  | Validação            | Script `validate_production.sh`       | Todos os checks `[OK]`            |


> **Fase F3 (produção escolar):** Qdrant, Redis e Docker estão previstos em `docs/REQUISITOS.md` (RNF07). A seção 12 deste documento descreve a preparação antecipada; a codificação Docker virá no agente RAG.

---

## 2. Requisitos de hardware

### 2.1 Perfis recomendados


| Perfil                           | Uso                            | CPU              | RAM       | Disco           | GPU                          | Rede               |
| -------------------------------- | ------------------------------ | ---------------- | --------- | --------------- | ---------------------------- | ------------------ |
| **Mínimo (dev/MVP)**             | Testes internos, poucos alunos | 4 núcleos x86_64 | **8 GB**  | 40 GB SSD       | Não (CPU)                    | 50 Mbps estável    |
| **Recomendado (piloto escolar)** | WhatsApp piloto, ~100 alunos   | 8 núcleos        | **16 GB** | 100 GB SSD NVMe | Opcional (ver abaixo)        | 100 Mbps           |
| **Produção (escola)**            | Carga contínua, reindexação    | 8–16 núcleos     | **32 GB** | 250 GB SSD NVMe | **6 GB+ VRAM** (recomendado) | 200 Mbps + IP fixo |


### 2.2 Componentes detalhados

#### Processador (CPU)

- Arquitetura **64 bits** (AMD64 / Intel x86_64).
- Mínimo: 4 núcleos físicos ou 4 vCPUs (VM).
- Recomendado: 8+ núcleos para inferência CPU + embeddings + API simultâneos.

#### Memória (RAM)

- **8 GB** — mínimo absoluto com LLM em CPU (latência alta, ver RNF11).
- **16 GB** — recomendado para MVP em produção com Ollama + Chroma + FastAPI.
- **32 GB** — produção com re-ranking, múltiplos workers Gunicorn e margem para indexação.

Estimativa de consumo (piloto):


| Componente                         | RAM aproximada |
| ---------------------------------- | -------------- |
| Ubuntu Server + serviços base      | 1–2 GB         |
| Ollama + Qwen2.5-Math-1.5B (CPU)   | 3–5 GB         |
| sentence-transformers (embeddings) | 1–2 GB         |
| FastAPI + Gunicorn (2 workers)     | 1–2 GB         |
| Chroma (índice até ~50k chunks)    | 0,5–2 GB       |
| **Total estimado**                 | **7–13 GB**    |


#### Disco

- Tipo: **SSD** (evite HDD para índice vetorial e modelos).
- Espaço mínimo:


| Item                            | Espaço                      |
| ------------------------------- | --------------------------- |
| Ubuntu Server LTS               | ~5 GB                       |
| Projeto + venv Python           | ~3 GB                       |
| Ollama (Qwen2.5-Math-1.5B)      | ~1,5 GB                     |
| Embeddings + cache Hugging Face | ~2 GB                       |
| Corpus PDF (`data/materials/`)  | 5–20 GB (depende da escola) |
| Índice Chroma                   | 1–10 GB                     |
| Logs, auditoria, backups        | 10+ GB                      |
| **Total mínimo**                | **~40 GB** livres           |
| **Recomendado**                 | **100 GB+** livres          |


#### GPU (opcional, acelera inferência)

- **Mínimo VRAM:** 6 GB (RNF09) — ex.: NVIDIA GTX 1660 Super, RTX 3060.
- **Recomendado:** 8–12 GB VRAM — ex.: RTX 3060 12 GB, RTX 4060.
- Driver NVIDIA + CUDA (se usar GPU com Ollama):

```bash
# Verificar GPU após instalar drivers
nvidia-smi
```

Sem GPU, o sistema funciona em CPU com latência maior (p95 geração < 20s aceitável com aviso — RNF11).

#### Rede

- **IP público fixo** ou DNS dinâmico (webhook WhatsApp exige HTTPS).
- Portas de entrada liberadas: **22** (SSH), **80** (HTTP/Let's Encrypt), **443** (HTTPS).
- Porta **8000** apenas local (Nginx faz proxy); **não** exponha 8000 na internet.
- Latência estável para APIs externas: Twilio/Meta, Asaas, LangSmith.

#### Máquina do painel Streamlit (opcional)

- Pode rodar em **outro PC** na rede da escola (arquitetura híbrida do README).
- Mínimo: 4 GB RAM, Python 3.11+, navegador web.
- Não precisa de GPU.

---

## 3. Fase 0 — Pré-requisitos (antes de ligar o servidor)

Anote tudo **antes** da instalação. Nesta fase você **não precisa** do servidor ligado ainda — só contas, chaves e (quando já souber o IP) o DNS.

**Prioridade prática:**

| Quando | Itens |
|--------|--------|
| **Obrigatório para WhatsApp em produção** | Domínio + DNS + `ADMIN_API_KEY` + Twilio **ou** Meta |
| **Obrigatório para painel / admin** | `ADMIN_API_KEY` |
| **Recomendado em produção** | LangSmith (tracing + auditoria técnica) |
| **Opcional** | Asaas (só se for cobrar assinatura / plano escola) |
| **Pode adiar** | Domínio e Twilio se for só testar RAG localmente (`uvicorn` + Ollama) |


| Item | Onde obter | Usado em |
|------|------------|----------|
| Domínio (ex.: `tutor.escola.edu.br`) | Registro.br / Cloudflare | Nginx + TLS + webhook |
| Conta LangSmith | https://smith.langchain.com | Tracing RAG |
| Conta Twilio **ou** Meta WhatsApp Cloud API | twilio.com / developers.facebook.com | Canal WhatsApp |
| Conta Asaas (opcional) | asaas.com | Cobrança |
| Chave `ADMIN_API_KEY` | Gere localmente: `openssl rand -hex 32` | API admin + painel |

---

### 3.1 Domínio (e registro DNS)

#### Para que serve no deepEdu

O WhatsApp (Twilio ou Meta) **não fala com `http://192.168.x.x`**. Ele exige um endereço **público HTTPS** para enviar mensagens ao servidor (webhook).

No projeto o domínio entra em:

| Uso | Onde |
|-----|------|
| Certificado TLS (Let's Encrypt via Certbot) | Fase 13 — Nginx |
| Virtual host Nginx (`server_name`) | `nginx/deepedu.conf.template` |
| URL pública da API | `.env` → `PUBLIC_BASE_URL=https://tutor.escola.edu.br` |
| Webhook WhatsApp | `https://SEU_DOMINIO/webhook/whatsapp` |
| Webhook Asaas (se usar) | `https://SEU_DOMINIO/webhook/asaas` |
| Painel Streamlit apontando para a nuvem | `control_panel/.env` → `CLOUD_API_BASE_URL` |

Sem domínio (ou sem HTTPS), o tutor pode rodar **só na rede local** para testes de RAG — mas **não** recebe mensagens reais do WhatsApp.

#### Passo a passo — obter o domínio

**Opção A — Registro.br (domínio `.br`)**

1. Acesse https://registro.br
2. Busque um nome disponível (ex.: `escola-alpha.com.br` ou subdomínio em domínio que a escola já tenha).
3. Crie/conta e finalize o registro (CPF/CNPJ da escola ou responsável).
4. Anote: nome do domínio e login do painel DNS.

**Opção B — Cloudflare (qualquer TLD + DNS fácil)**

1. Acesse https://dash.cloudflare.com e crie conta.
2. Compre o domínio na Cloudflare **ou** aponte um domínio já comprado (Registro.br, GoDaddy etc.) para os nameservers da Cloudflare.
3. No painel Cloudflare → **DNS** → você criará o registro A (abaixo).

**Subdomínio (recomendado):** use algo como `tutor.escola.edu.br` em vez do domínio raiz — facilita separar o site institucional do tutor.

#### Passo a passo — registro DNS (Tipo A)

Só faça isto **depois** de saber o **IP público** do servidor (Fase 1+):

1. No painel DNS do provedor, crie:

```
Tipo: A
Nome/Host: tutor          (ou @ se for o domínio raiz)
Conteúdo/Valor: IP_PUBLICO_DO_SERVIDOR
TTL: automático ou 300
```

2. Resultado esperado: `tutor.escola.edu.br` resolve para o IP do Ubuntu Server.
3. Confira depois (de qualquer PC):

```bash
getent hosts tutor.escola.edu.br
# ou
dig +short tutor.escola.edu.br
```

4. No `.env` do deepEdu (Fase 8 / produção):

```env
PUBLIC_BASE_URL=https://tutor.escola.edu.br
```

> **Firewall:** liberar portas **80** e **443** no servidor e no roteador/cloud (Security Group). O Certbot usa a 80 na emissão do certificado.

#### Checklist — anote

```
[ ] Domínio: _______________________________
[ ] Subdomínio do tutor: ___________________
[ ] Provedor DNS: __________________________
[ ] IP público do servidor (quando souber): _
```

---

### 3.2 Conta LangSmith

#### Para que serve no deepEdu

LangSmith é a plataforma de **observabilidade** do ecossistema LangChain. No deepEdu ela grava o **rastreamento (trace)** de cada execução do pipeline RAG:

- pergunta do aluno
- chunks recuperados e scores
- prompt montado
- resposta do LLM
- latência e erros

No código isso aparece em:

| Peça | Função |
|------|--------|
| `.env` → `LANGCHAIN_TRACING_V2=true` | Liga o tracing |
| `.env` → `LANGSMITH_API_KEY` | Autentica no LangSmith |
| `.env` → `LANGCHAIN_PROJECT` | Nome do projeto (ex.: `deepedu-prod`) |
| `app/core/langsmith_setup.py` | Configura as variáveis de ambiente |
| `app/rag/chain.py` / `tutor_service.py` | Dispara traces nas cadeias |
| Auditoria ECA | Guarda `langsmith_run_id` no `audit_log` (complementa o log local — RF31 / RF47) |

**Em desenvolvimento offline** você pode deixar `LANGCHAIN_TRACING_V2=false` e não precisar da conta.  
**Em produção / piloto** o requisito recomenda tracing ligado para depurar respostas ruins e auditar o fluxo.

#### Passo a passo — criar conta e API key

1. Acesse https://smith.langchain.com
2. Crie conta (e-mail, Google ou GitHub).
3. Aceite os termos e entre no painel.
4. Vá em **Settings** (engrenagem) → **API Keys** (ou **Access & Sharing** → API Keys, conforme a UI atual).
5. Clique em **Create API Key**, dê um nome (ex.: `deepedu-prod`) e copie a chave **na hora** (formato típico: `lsv2_pt_...`).
6. No LangSmith, crie/selecione um **Project** com o mesmo nome que usará no `.env` (ex.: `deepedu-prod`).
7. Cole no `.env` do servidor:

```env
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_pt_cole_sua_chave_aqui
LANGCHAIN_PROJECT=deepedu-prod
```

8. Após a API estar no ar, faça uma pergunta de teste e confira em https://smith.langchain.com se o run apareceu no projeto.

#### Checklist — anote

```
[ ] E-mail da conta LangSmith: _____________
[ ] API Key gerada e guardada em cofre: ____
[ ] Nome do projeto: deepedu-prod (ou outro)
```

> **Segurança:** nunca commite a API key no Git. Só no `.env` com permissão `chmod 600`.

---

### 3.3 Conta Twilio (ou Meta WhatsApp Cloud API)

O deepEdu fala com o aluno pelo **WhatsApp**. O código aceita dois provedores (`WHATSAPP_PROVIDER` no `.env`):

| Provedor | Quando usar | Variável |
|----------|-------------|----------|
| **Twilio** (padrão no projeto) | Mais simples para piloto; sandbox + número Twilio | `WHATSAPP_PROVIDER=twilio` |
| **Meta Cloud API** | Conta Business oficial da escola / BSP | `WHATSAPP_PROVIDER=meta` |

Abaixo o detalhe do **Twilio** (caminho mais usado no README atual). Meta fica resumido no final desta seção.

#### Para que serve Twilio no deepEdu

| Fluxo | O que acontece |
|-------|----------------|
| Aluno manda mensagem no WhatsApp | Twilio recebe e faz **POST** em `https://SEU_DOMINIO/webhook/whatsapp` |
| deepEdu processa (consentimento, billing, RAG) | Gera a resposta do tutor |
| deepEdu responde | Usa a API Twilio para enviar a mensagem de volta ao aluno |
| Script `configure_twilio_webhook.py` | Configura automaticamente a URL do webhook no número Twilio |

Credenciais usadas no `.env`:

| Variável | Significado |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | ID da conta (`AC...`) |
| `TWILIO_AUTH_TOKEN` | Segredo da conta |
| `TWILIO_WHATSAPP_NUMBER` | Número no formato `whatsapp:+1...` ou BR |
| `TWILIO_PHONE_NUMBER_SID` | SID do número (`PN...`) — usado pelo script de webhook |
| `TWILIO_VALIDATE_SIGNATURE` | Valida se o POST veio mesmo da Twilio |
| `PUBLIC_BASE_URL` | Base HTTPS onde está o webhook |

Também: números de professor em `PROFESSOR_WHATSAPP_NUMBERS` (comandos administrativos via WhatsApp).

#### Passo a passo — criar conta Twilio e WhatsApp

1. Acesse https://www.twilio.com/try-twilio e crie conta (e-mail + verificação).
2. No Console Twilio, anote em **Account → API keys & tokens** (ou dashboard inicial):
   - **Account SID**
   - **Auth Token** (Reveal / Show)
3. Ative o canal WhatsApp:
   - Vá em **Messaging → Try it out → Send a WhatsApp message** (Sandbox) **ou**
   - **Messaging → Senders → WhatsApp senders** para número de produção.
4. **Sandbox (piloto rápido):**
   - Anote o número do sandbox Twilio (ex.: `whatsapp:+14155238886`).
   - No celular, envie o código de join (ex.: `join xxxx-xxxx`) para o número indicado no console.
   - Só números que “entraram” no sandbox recebem/enviam mensagens.
5. **Produção:** solicite um WhatsApp Sender aprovado (documento da empresa/escola, Meta Business). Tempo e aprovação variam.
6. Anote o **Phone Number SID** (`PN...`):
   - Console → **Phone Numbers → Manage → Active numbers** → clique no número → copie o SID.
7. Preencha no `.env` (depois que o HTTPS existir):

```env
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_PHONE_NUMBER_SID=PNxxxxxxxxxxxxxxxx
TWILIO_VALIDATE_SIGNATURE=true
PUBLIC_BASE_URL=https://tutor.escola.edu.br
```

8. Com o servidor e HTTPS no ar (Fase 13+):

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate
python scripts/configure_twilio_webhook.py
```

Isso aponta o webhook para `https://SEU_DOMINIO/webhook/whatsapp`.

#### Alternativa — Meta WhatsApp Cloud API (resumo)

1. Conta em https://developers.facebook.com
2. Crie um **App** tipo Business + produto **WhatsApp**.
3. Vincule um **Meta Business Portfolio** e um número de telefone.
4. Gere **Access Token**, anote **Phone number ID**, **App Secret** e defina um **Verify Token** seu.
5. No `.env`:

```env
WHATSAPP_PROVIDER=meta
META_VERIFY_TOKEN=escolha_um_token_secreto
META_APP_SECRET=seu_app_secret
META_ACCESS_TOKEN=seu_access_token
META_PHONE_NUMBER_ID=seu_phone_number_id
PUBLIC_BASE_URL=https://tutor.escola.edu.br
```

6. No painel Meta, configure o webhook para `https://SEU_DOMINIO/webhook/whatsapp` (ou rota Meta do projeto, conforme implementação).

#### Checklist — anote (Twilio)

```
[ ] Account SID (AC...): ___________________
[ ] Auth Token: (só no cofre) ______________
[ ] WhatsApp number: whatsapp:+____________
[ ] Phone Number SID (PN...): ______________
[ ] Sandbox join feito no celular de teste: _
```

---

### 3.4 Conta Asaas (opcional — cobrança)

#### Para que serve no deepEdu

Asaas é o **gateway de pagamento brasileiro** já integrado. Só é necessário se você for **cobrar** alunos ou escolas.

Fluxos no projeto:

| Função | Como |
|--------|------|
| Checkout individual (PIX, boleto, cartão) | Endpoints `/admin/billing/checkout` e comando WhatsApp `pagar` |
| Checkout plano escola (B2B) | `/admin/schools/checkout` |
| Ativação automática da assinatura | Webhook `POST /webhook/asaas` quando o pagamento confirma |
| Bloqueio sem pagamento | `BILLING_ENFORCE_SUBSCRIPTION=true` no `.env` |

Sem Asaas você ainda pode:

- rodar o tutor completo
- usar `trial` / ativação manual via admin (`/admin/billing/activate`)
- deixar cobrança para depois

Variáveis no `.env`:

| Variável | Uso |
|----------|-----|
| `ASAAS_API_KEY` | Autentica chamadas à API Asaas |
| `ASAAS_BASE_URL` | `https://api.asaas.com/v3` (produção) ou sandbox |
| `ASAAS_WEBHOOK_TOKEN` | Token que o Asaas envia no header; deepEdu valida em `/webhook/asaas` |
| `ASAAS_BILLING_AMOUNT` | Valor padrão do plano aluno (ex.: `29.90`) |
| `ASAAS_DEFAULT_BILLING_TYPE` | `UNDEFINED` = aluno escolhe PIX/boleto/cartão no checkout |
| `SCHOOL_PLAN_AMOUNT` / `SCHOOL_PLAN_DAYS` | Plano escola |

#### Passo a passo — criar conta e chaves

1. Acesse https://www.asaas.com e crie conta (CNPJ da escola/empresa recomendado para produção).
2. Complete o onboarding (dados bancários, documentos) para receber pagamentos reais.
3. Para **testes**, use o ambiente **Sandbox** (conta de homologação no painel Asaas) — não mexe em dinheiro real.
4. No painel: **Integrações → API Key** (ou **Minha Conta → Integração**):
   - Gere / copie a **API Key**.
5. Crie um **Webhook**:
   - URL: `https://SEU_DOMINIO/webhook/asaas` (precisa do domínio HTTPS já ativo).
   - Eventos: pagamento confirmado/recebido/vencido/estornado (os tratados no código: `PAYMENT_CONFIRMED`, `PAYMENT_RECEIVED`, `PAYMENT_OVERDUE`, etc.).
   - Defina um **access token** / autenticação do webhook e use o **mesmo valor** em `ASAAS_WEBHOOK_TOKEN`.
6. No `.env`:

```env
ASAAS_API_KEY=sua_chave_asaas
ASAAS_BASE_URL=https://api.asaas.com/v3
ASAAS_WEBHOOK_TOKEN=mesmo_token_do_painel
ASAAS_BILLING_AMOUNT=29.90
ASAAS_DEFAULT_BILLING_TYPE=UNDEFINED
BILLING_ENFORCE_SUBSCRIPTION=false
PUBLIC_BASE_URL=https://tutor.escola.edu.br
```

7. Comece com `BILLING_ENFORCE_SUBSCRIPTION=false`. Só mude para `true` quando o fluxo de pagamento estiver testado.

#### Checklist — anote

```
[ ] Conta Asaas (prod / sandbox): __________
[ ] API Key guardada: ______________________
[ ] Token do webhook: ______________________
[ ] Valor plano aluno: R$ __________________
[ ] Cobrança obrigatória agora? (s/n) ______
```

---

### 3.5 Chave `ADMIN_API_KEY`

#### Para que serve no deepEdu

É a **senha secreta da API administrativa**. Não é login de usuário humano com senha no banco — é uma chave que o cliente (painel Streamlit, `curl`, scripts) envia no header HTTP:

```http
X-Admin-Api-Key: sua_chave_aqui
```

Protege ações sensíveis, por exemplo:

- ativar assinatura / gerar checkout
- criar escola e vincular aluno
- endpoints em `app/api/admin.py`
- painel Streamlit (`control_panel/streamlit_app.py` lê a mesma chave)

No código:

| Arquivo | Papel |
|---------|--------|
| `app/core/security.py` → `require_admin_api_key` | Compara o header com `.env`; 403 se errado |
| `app/core/startup_checks.py` | Em **produção**, exige chave com pelo menos 16 caracteres |
| `control_panel/.env` | Deve ter a **mesma** chave do servidor |

Quem tem essa chave controla billing, escolas e operações admin — trate como senha de root.

#### Passo a passo — gerar e configurar

1. Em qualquer Linux/macOS (ou no próprio servidor depois de instalado):

```bash
openssl rand -hex 32
```

Exemplo de saída (não use esta — gere a sua):

```
a3f1c9e8b2d04765...   # 64 caracteres hex
```

2. Guarde em um cofre (Bitwarden, 1Password, papel no cofre da escola — **não** no WhatsApp/e-mail).
3. No servidor, no `.env` do deepEdu:

```env
ADMIN_API_KEY=cole_aqui_o_resultado_do_openssl
```

4. No painel local, em `control_panel/.env`:

```env
CLOUD_API_BASE_URL=https://tutor.escola.edu.br
ADMIN_API_KEY=mesma_chave_do_servidor
```

5. Restrinja permissão do arquivo:

```bash
chmod 600 ~/Projects/deepEdu/.env
chmod 600 ~/Projects/deepEdu/control_panel/.env
```

6. Teste (com API no ar):

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "X-Admin-Api-Key: SUA_CHAVE" \
  "http://127.0.0.1:8000/admin/..."
```

Sem a chave correta → **403**. Chave fraca ou ausente em produção → a aplicação **recusa subir** (`ProductionConfigError`).

#### Checklist — anote

```
[ ] ADMIN_API_KEY gerada com openssl
[ ] Copiada no .env do servidor
[ ] Mesma chave no control_panel/.env
[ ] Arquivos .env com chmod 600
[ ] Ninguém commitou no Git
```

---

### 3.6 Resumo — o que anotar num único bloco

```
=== deepEdu Fase 0 ===
Domínio:              ______________________________
PUBLIC_BASE_URL:      https://______________________
IP servidor (depois): ______________________________

LangSmith e-mail:     ______________________________
LANGSMITH_API_KEY:    (cofre)
LANGCHAIN_PROJECT:    deepedu-prod

Twilio Account SID:   AC____________________________
Twilio Auth Token:    (cofre)
WhatsApp number:      whatsapp:+____________________
Phone Number SID:     PN____________________________

Asaas (opcional):     [ ] não usar agora
ASAAS_API_KEY:        (cofre)
ASAAS_WEBHOOK_TOKEN:  (cofre)

ADMIN_API_KEY:        (cofre — openssl rand -hex 32)
```

Quando este bloco estiver preenchido (mínimo: `ADMIN_API_KEY`; para WhatsApp: domínio + Twilio/Meta), avance para a **Fase 1 — Ubuntu Server LTS**.

---


## 4. Fase 1 — Instalação do Ubuntu Server LTS

### 4.1 Mídia de instalação

1. Baixe a ISO em: [https://ubuntu.com/download/server](https://ubuntu.com/download/server)
2. Escolha **Ubuntu Server 24.04 LTS** (ou 22.04 LTS).
3. Grave em pendrive com Ventoy, Rufus ou `dd`.

### 4.2 Instalação interativa (resumo)

Durante o instalador, configure:


| Tela    | Escolha recomendada                                |
| ------- | -------------------------------------------------- |
| Idioma  | Português ou English                               |
| Teclado | Brazilian ou US                                    |
| Tipo    | Ubuntu Server                                      |
| Rede    | IP estático (produção) ou DHCP (lab)               |
| Proxy   | Deixe em branco (salvo proxy escolar)              |
| Mirror  | Padrão                                             |
| Disco   | Usar disco inteiro + LVM (ou partição manual)      |
| Perfil  | Seu nome, hostname `deepedu-srv`, usuário `edidio` |
| SSH     | **Marcar "Install OpenSSH server"**                |
| Snaps   | Nenhum extra necessário                            |


### 4.3 Primeiro login

```bash
# Do seu PC local
ssh edidio@IP_DO_SERVIDOR
```

### 4.4 Verificar versão

```bash
lsb_release -a
uname -m
```

Saída esperada: `Ubuntu 24.04.x LTS` ou `22.04.x LTS`, arquitetura `x86_64`.

---

## 5. Fase 2 — Configuração base do sistema

Execute como usuário com `sudo`:

```bash
# Atualizar pacotes
sudo apt update
sudo apt upgrade -y

# Pacotes essenciais
sudo apt install -y \
  curl \
  wget \
  git \
  vim \
  htop \
  unzip \
  ca-certificates \
  gnupg \
  lsb-release \
  software-properties-common \
  apt-transport-https

# Definir fuso horário (Brasil)
sudo timedatectl set-timezone America/Sao_Paulo

# Verificar
timedatectl
```

### 5.1 Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

### 5.2 (Opcional) IP estático via Netplan

Edite o arquivo em `/etc/netplan/` (nome varia):

```bash
sudo nano /etc/netplan/00-installer-config.yaml
```

Exemplo:

```yaml
network:
  version: 2
  ethernets:
    ens18:
      dhcp4: false
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Aplique:

```bash
sudo netplan apply
```

---

## 6. Fase 3 — Python 3.11 e dependências de sistema

O deepEdu usa Python 3.11+. No Ubuntu 24.04:

```bash
sudo apt install -y \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  python3-pip \
  build-essential \
  pkg-config \
  libffi-dev \
  libssl-dev \
  poppler-utils
```

No Ubuntu **22.04** (Python 3.10 padrão), adicione o PPA deadsnakes:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  python3-pip \
  build-essential \
  pkg-config \
  libffi-dev \
  libssl-dev \
  poppler-utils
```

Verificar:

```bash
python3.11 --version
pdftoppm -v
```

### 6.1 (Opcional) OCR para PDFs escaneados — Fase posterior

```bash
sudo apt install -y tesseract-ocr tesseract-ocr-por
tesseract --version
```

---

## 7. Fase 4 — Clonar o projeto

```bash
mkdir -p ~/Projects
cd ~/Projects

# Via HTTPS
git clone https://github.com/SEU_USUARIO/deepEdu.git deepEdu

# OU via SSH
# git clone git@github.com:SEU_USUARIO/deepEdu.git deepEdu

cd ~/Projects/deepEdu
ls -la
```

Se o código já estiver no servidor (pendrive, scp):

```bash
mkdir -p ~/Projects
scp -r usuario@origem:/caminho/deepEdu ~/Projects/deepEdu
cd ~/Projects/deepEdu
```

---

## 8. Fase 5 — Ambiente Python virtual

```bash
cd ~/Projects/deepEdu

python3.11 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

Verificar LangChain instalado:

```bash
python -c "import langchain; import langchain_core; print('langchain', langchain.__version__)"
python -c "import fastapi; import chromadb; print('fastapi e chromadb OK')"
```

> **Nota:** A instalação de `torch` e `sentence-transformers` pode levar vários minutos e ~2 GB de download.

---

## 9. Fase 6 — Ollama + modelo Qwen2.5-Math (LLM)

O projeto usa **Ollama** como provedor padrão de LLM (`LLM_PROVIDER=ollama`).

### 9.1 Instalação automática (script do projeto)

```bash
cd ~/Projects/deepEdu
chmod +x scripts/install_ollama_model.sh
./scripts/install_ollama_model.sh
```

### 9.2 Instalação manual (comandos explícitos)

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar serviço
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama

# Baixar modelo matemático (RNF09 / RF14)
ollama pull qwen2.5-math:1.5b-instruct

# Listar modelos
ollama list
```

### 9.3 Teste rápido do modelo

```bash
ollama run qwen2.5-math:1.5b-instruct "Resolva: qual é a derivada de x^2 + 3x?"
```

Saída esperada: explicação matemática em português ou inglês.

### 9.4 (Opcional) GPU NVIDIA com Ollama

```bash
# Instalar driver (Ubuntu 24.04)
sudo apt install -y nvidia-driver-535
sudo reboot

# Após reboot
nvidia-smi
ollama run qwen2.5-math:1.5b-instruct "2+2=?"
```

---

## 10. Fase 7 — Modelo de embeddings

O modelo padrão está em `.env.example`:

```
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Pré-baixar (evita demora na primeira indexação):

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate

python << 'PY'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
print("Embeddings OK, dimensão:", model.get_sentence_embedding_dimension())
PY
```

---

## 11. Fase 8 — Arquivo `.env`

```bash
cd ~/Projects/deepEdu
cp .env.example .env
chmod 600 .env
nano .env
```

### 11.1 Variáveis mínimas para MVP local

```env
APP_NAME=deepEdu
ENV=development
HOST=0.0.0.0
PORT=8000

# LLM local
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-math:1.5b-instruct
OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_TEMPERATURE=0.3
LLM_MAX_NEW_TOKENS=1024

# RAG / tokens
PROMPT_FILE=prompts/v1_tutor_em.md
PROMPT_MAX_TOKENS=400
RAG_CONTEXT_MAX_TOKENS=1200
HISTORY_MAX_TOKENS=800
RETRIEVAL_TOP_K=3

# Embeddings e Chroma
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHROMA_DIR=./data/chroma
MATERIALS_DIR=./data/materials

# Segurança
ADMIN_API_KEY=COLE_AQUI_OUTPUT_DE_openssl_rand_hex_32
AUDIT_PHONE_SALT=COLE_AQUI_OUTRO_SALT_LONGO_ALEATORIO
AUDIT_FAIL_CLOSED=true

# LangSmith (false em dev offline)
LANGCHAIN_TRACING_V2=false
```

Gerar chaves:

```bash
openssl rand -hex 32    # ADMIN_API_KEY
openssl rand -hex 32    # AUDIT_PHONE_SALT
```

### 11.2 Variáveis para produção (preencher ao avançar)

```env
ENV=production
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=sua_chave_langsmith
LANGCHAIN_PROJECT=deepedu-prod
PUBLIC_BASE_URL=https://tutor.escola.edu.br

# WhatsApp (escolha um provedor)
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 12. Fase 9 — LangSmith (observabilidade)

1. Crie conta em [https://smith.langchain.com](https://smith.langchain.com)
2. Gere API key em **Settings → API Keys**
3. No `.env`:

```env
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxx
LANGCHAIN_PROJECT=deepedu-prod
```

1. Teste após subir a API (Fase 12) — traces aparecem no painel LangSmith.

---

## 13. Fase 10 — Banco vetorial Chroma (MVP)

Chroma roda **embutido** no processo Python (sem serviço separado no MVP).

```bash
cd ~/Projects/deepEdu
mkdir -p data/chroma data/materials data/chat_history data/billing data/audit
ls -la data/
```

Para **produção F3** (Qdrant via Docker — preparação antecipada):

```bash
# Instalar Docker (quando for usar Qdrant)
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# Faça logout e login para aplicar o grupo docker

# Subir Qdrant (quando o código suportar VECTOR_STORE_PROVIDER=qdrant)
docker run -d \
  --name qdrant \
  --restart unless-stopped \
  -p 6333:6333 \
  -v /opt/deepedu/qdrant:/qdrant/storage \
  qdrant/qdrant:latest

curl http://127.0.0.1:6333/readyz
```

---

## 14. Fase 11 — Corpus didático

Copie materiais para o servidor:

```bash
# Exemplo: enviar PDFs do seu PC
scp -r ./materiais/*.pdf edidio@IP_SERVIDOR:~/Projects/deepEdu/data/materials/

# No servidor
ls -lh ~/Projects/deepEdu/data/materials/
```

Formatos suportados: `.pdf`, `.txt`, `.md` (ver RF15).

Indexação (executar **após** Fases 5–10 concluídas):

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate
python scripts/run_indexing.qundopy
```

---

## 15. Fase 12 — API FastAPI (teste manual)

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

Em **outro terminal** (ou do seu PC):

```bash
curl -s http://IP_SERVIDOR:8000/health | python3 -m json.tool
```

Testes unitários:

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Pare o uvicorn manual (`Ctrl+C`) antes da Fase 13.

---

## 16. Fase 13 — Produção: systemd + Nginx + HTTPS

Substitua:

- `SEU_DOMINIO` → ex. `tutor.escola.edu.br`
- `SEU_USUARIO` → ex. `edidio`

### 16.1 Opção automática (recomendada)

```bash
cd ~/Projects/deepEdu
chmod +x scripts/setup_production.sh
./scripts/setup_production.sh SEU_DOMINIO SEU_USUARIO
```

### 16.2 Opção manual (comandos explícitos)

```bash
# Nginx + Certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# Systemd
cd ~/Projects/deepEdu
sudo sed "s|SEU_USUARIO|SEU_USUARIO|g" systemd/deepedu.service | sudo tee /etc/systemd/system/deepedu.service
sudo systemctl daemon-reload
sudo systemctl enable deepedu
sudo systemctl start deepedu
sudo systemctl status deepedu

# Nginx virtual host
sudo sed "s|__DOMAIN__|SEU_DOMINIO|g" nginx/deepedu.conf.template | sudo tee /etc/nginx/sites-available/deepedu
sudo ln -sf /etc/nginx/sites-available/deepedu /etc/nginx/sites-enabled/deepedu
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# TLS Let's Encrypt
sudo certbot --nginx -d SEU_DOMINIO --non-interactive --agree-tos --register-unsafely-without-email --redirect

# Verificar
curl -I https://SEU_DOMINIO/health
```

Logs:

```bash
journalctl -u deepedu -f
sudo tail -f /var/log/nginx/access.log
```

---

## 17. Fase 14 — Painel web Streamlit (interface gráfica)

O painel administrativo fica em `control_panel/`. Pode rodar **no servidor** ou **em PC local** da escola.

### 17.1 No servidor (mesma máquina)

```bash
cd ~/Projects/deepEdu/control_panel
cp .env.example .env
nano .env
```

Conteúdo de `.env`:

```env
CLOUD_API_BASE_URL=https://SEU_DOMINIO
ADMIN_API_KEY=mesma_chave_do_servidor
```

Instalar e executar:

```bash
cd ~/Projects/deepEdu/control_panel
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-control.txt
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

Acesse: `http://IP_SERVIDOR:8501`

> Em produção, coloque o Streamlit atrás de Nginx com autenticação ou restrinja ao IP da escola via UFW.

### 17.2 Em PC local da escola (arquitetura híbrida)

No PC Windows/Linux da coordenação:

```bash
cd ~/Projects/deepEdu/control_panel
cp .env.example .env
# CLOUD_API_BASE_URL=https://tutor.escola.edu.br
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-control.txt
streamlit run streamlit_app.py
```

---

## 18. Fase 15 — WhatsApp (Twilio)

Após HTTPS ativo e `PUBLIC_BASE_URL` no `.env`:

```bash
cd ~/Projects/deepEdu
source .venv/bin/activate
python scripts/configure_twilio_webhook.py
```

Webhook público:

```
https://SEU_DOMINIO/webhook/whatsapp
```

Configure no console Twilio o mesmo URL.

### Alternativa: Meta WhatsApp Cloud API

No `.env`:

```env
WHATSAPP_PROVIDER=meta
META_VERIFY_TOKEN=seu_token_verificacao
META_APP_SECRET=seu_app_secret
META_ACCESS_TOKEN=seu_access_token
META_PHONE_NUMBER_ID=seu_phone_number_id
```

---

## 19. Fase 16 — Validação final

```bash
cd ~/Projects/deepEdu
chmod +x scripts/validate_production.sh
./scripts/validate_production.sh SEU_DOMINIO
```

Checklist manual:

```bash
# Serviços
sudo systemctl is-active deepedu
sudo systemctl is-active nginx
sudo systemctl is-active ollama

# Portas locais
sudo ss -ltnp | grep -E ':8000|:80|:443|:11434 '

# Health
curl -s https://SEU_DOMINIO/health

# Modelo LLM
ollama list | grep qwen2.5-math

# Índice
ls -la ~/Projects/deepEdu/data/chroma/
```

---

## 20. Resumo da stack instalada


| Camada          | Software                          | Versão / nota      |
| --------------- | --------------------------------- | ------------------ |
| SO              | Ubuntu Server LTS                 | 22.04 ou 24.04     |
| Runtime         | Python                            | 3.11+              |
| API web         | FastAPI + Uvicorn/Gunicorn        | `requirements.txt` |
| Orquestração IA | LangChain + LangGraph + LangSmith | `requirements.txt` |
| LLM             | Ollama + Qwen2.5-Math-1.5B        | Local              |
| Embeddings      | sentence-transformers             | HF cache           |
| Vetorial (MVP)  | ChromaDB                          | Embutido           |
| Vetorial (F3)   | Qdrant                            | Docker             |
| Proxy/TLS       | Nginx + Certbot                   | Sistema            |
| Painel admin    | Streamlit                         | `control_panel/`   |
| WhatsApp        | Twilio ou Meta Cloud API          | Webhook HTTPS      |
| Pagamentos      | Asaas (opcional)                  | API REST           |


---

## 21. Troubleshooting rápido


| Sintoma                     | Comando de diagnóstico         | Solução comum                                               |
| --------------------------- | ------------------------------ | ----------------------------------------------------------- |
| API não sobe                | `journalctl -u deepedu -n 50`  | Verificar `.env` e `.venv` no systemd                       |
| Ollama lento                | `htop`                         | Pouca RAM; usar GPU ou reduzir workers                      |
| `ollama: command not found` | `sudo systemctl status ollama` | Reinstalar: `curl -fsSL https://ollama.com/install.sh | sh` |
| Erro ao ler PDF             | `pdftoppm -v`                  | `sudo apt install poppler-utils`                            |
| Certbot falha               | `sudo certbot certificates`    | DNS A record deve apontar para o servidor                   |
| Webhook 403                 | Logs nginx + app               | Conferir `PUBLIC_BASE_URL` e assinatura Twilio              |
| Indexação lenta             | —                              | Normal na 1ª vez (download embeddings)                      |


---

## 22. Próximo passo: agente de codificação RAG

Com **todas as fases 0–16 concluídas** e validação OK:

1. Abra um **novo agente** no Cursor apontando para `~/Projects/deepEdu`
2. Informe que a infraestrutura está pronta
3. O próximo trabalho é codificação/implementação do pipeline RAG (ingestão, retriever híbrido, LangGraph, testes `eval_rag.py`)

Documentos de referência para o agente RAG:

- `docs/REQUISITOS.md` — RF01–RF47
- `docs/TOKEN_BUDGET.md` — orçamento Qwen 4K
- `docs/AUDITORIA_ECA.md` — eventos obrigatórios
- `docs/eval/dataset_rag_matematica_em.csv` — 50 perguntas de teste

---

## Histórico


| Versão | Data       | Alteração                                                            |
| ------ | ---------- | -------------------------------------------------------------------- |
| 1.1    | 22/07/2026 | Fase 0 expandida: para que serve + passo a passo de cada pré-requisito |
| 1.0    | 01/07/2026 | Documento inicial — hardware + instalação ordenada Ubuntu Server LTS |


