# Instalação offline — passo a passo

## No PC **com internet** (antes de levar o pendrive)

Execute na pasta do projeto:

```bash
cd ~/Projects/deepEdu
chmod +x scripts/prepare_pendrive.sh
./scripts/prepare_pendrive.sh --with-wheels /caminho/do/pendrive
```

Isso copia o projeto + baixa os pacotes Python em `offline/wheels/`.

---

## No PC **sem internet**

### Passo 1 — Copiar do pendrive

```bash
mkdir -p ~/Projects
cp -r /media/$USER/NOME_DO_PENDRIVE/deepEdu ~/Projects/deepEdu
cd ~/Projects/deepEdu
```

### Passo 2 — Sistema

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip poppler-utils build-essential
```

### Passo 3 — Ambiente Python

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install --no-index --find-links=offline/wheels -r offline/requirements-offline.txt
```

### Passo 4 — Ollama (LLM local)

Instale Ollama pelo instalador incluído ou copie do site em outro PC:

```bash
bash scripts/install_ollama_model.sh
```

### Passo 5 — Configurar

```bash
cp .env.example .env
nano .env
```

Mínimo para dev offline:

```env
ENV=development
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-math:1.5b-instruct
LANGCHAIN_TRACING_V2=false
AUDIT_PHONE_SALT=seu-salt-longo-aqui-min-16
ADMIN_API_KEY=sua-chave-admin-forte
```

### Passo 6 — Corpus e índice

```bash
# Copie PDFs da escola para data/materials/
python scripts/run_indexing.py
```

### Passo 7 — Rodar

```bash
uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

---

## Verificação

```bash
python -m unittest discover -s tests -v
curl http://127.0.0.1:8000/health
```

Se tudo OK, pode codificar offline normalmente.
