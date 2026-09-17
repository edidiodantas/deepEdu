# deepEdu — Pacote para PC offline (pendrive)

Leia este arquivo **no PC sem internet** antes de instalar.

---

## 1. O que vem neste pendrive

| Item | Descrição |
|------|-----------|
| `deepEdu/` | Código-fonte, documentação, testes, scripts |
| `DOCUMENTO_FINAL_deepEdu.pdf` | Documento completo (requisitos + casos de uso) |
| `deepEdu/offline/wheels/` | Pacotes Python (se foi gerado com `--with-wheels`) |
| `deepEdu-offline-*.tar.gz` | Cópia compactada de backup |

---

## 2. Requisitos no PC destino

- **Ubuntu 22.04+** (ou Debian similar)
- **Python 3.10+** (`python3`)
- **8 GB RAM** mínimo (16 GB recomendado)
- Internet na **1ª vez** para baixar Amadeus-Verbo (`scripts/install_hf_model.sh`)
- Depois do cache, o RAG roda localmente sem API paga de LLM

---

## 3. Instalação rápida (PC offline)

```bash
# 1. Copie a pasta deepEdu do pendrive para o PC
cp -r /media/SEU_USUARIO/PENDRIVE/deepEdu ~/Projects/deepEdu
cd ~/Projects/deepEdu

# 2. Python venv
sudo apt install -y python3-venv python3-pip poppler-utils
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependências (com wheels offline)
pip install --no-index --find-links=offline/wheels -r offline/requirements-offline.txt

# Se não houver pasta wheels/, no PC com internet (antes de desconectar):
# pip install -r requirements.txt

# 4. Configuração
cp .env.example .env
# Edite .env: AUDIT_PHONE_SALT, PHONE_ENCRYPTION_KEY, ADMIN_API_KEY

# 5. Modelo Amadeus-Verbo (precisa internet na 1ª vez)
bash scripts/install_hf_model.sh

# 6. Materiais didáticos
# Coloque PDFs em data/materials/ e indexe:
python scripts/run_indexing.py

# 7. Subir API
source .venv/bin/activate
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

---

## 4. Testes sem internet

```bash
source .venv/bin/activate
python -m unittest discover -s tests -p "test_*.py" -v
curl http://127.0.0.1:8000/health
```

---

## 5. Documentação importante

| Arquivo | Conteúdo |
|---------|----------|
| `docs/REQUISITOS.md` | RF e RNF |
| `docs/CASOS_DE_USO.md` | 64 casos de uso |
| `docs/REVISAO_IMPLEMENTACAO.md` | Status da implementação |
| `docs/output/DOCUMENTO_FINAL.pdf` | PDF completo |

---

## 6. O que NÃO funciona offline

- Webhooks WhatsApp (precisa internet + domínio público)
- LangSmith (opcional; desligue `LANGCHAIN_TRACING_V2=false`)
- Pagamentos Asaas
- 1º download do Amadeus-Verbo / embeddings (depois ficam em cache local)

Para desenvolver offline (após cache): API local, testes, indexação, RAG com Amadeus-Verbo.

---

## 7. Suporte

Projeto: **deepEdu** — Tutor RAG Matemática Ensino Médio  
Versão do pacote: verifique a data na pasta `deepEdu-offline-*.tar.gz`.
