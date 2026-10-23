from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "DeepEdu"
    ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # LLM — Amadeus-Verbo 0,5B (Qwen2.5 PT-BR) via Hugging Face.
    # Tamanho de tese: cabe em notebook modesto. GPU acelera; CPU funciona.
    LLM_PROVIDER: str = "huggingface"
    LLM_MODEL: str = "amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    LLM_DEVICE_MAP: str = "auto"
    # auto = bfloat16 em GPU RTX 30+, float16 em GPU mais antiga, float32 na CPU.
    # Forçar: float32 | float16 | bfloat16
    LLM_DTYPE: str = "auto"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_NEW_TOKENS: int = 1024
    # Id do tokenizer (vazio = usa o proprio LLM_MODEL no Hugging Face).
    LLM_TOKENIZER_ID: str = "amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct"
    # 1 = usa só modelos já baixados (instalação offline pelo pendrive).
    # Lido pelo huggingface_hub no ambiente; scripts/iniciar.sh exporta a partir do .env.
    HF_HUB_OFFLINE: bool = False

    # Legado DeepSeek (fallback openai_compatible)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Prompt e orcamento de tokens (RF46)
    PROMPT_FILE: str = "prompts/v1_tutor_em.md"
    PROMPT_MAX_TOKENS: int = 400
    RAG_CONTEXT_MAX_TOKENS: int = 1200
    HISTORY_MAX_TOKENS: int = 800
    HISTORY_SUMMARY_TRIGGER: int = 600
    USER_MESSAGE_MAX_TOKENS: int = 400
    RETRIEVAL_TOP_K: int = 3
    RETRIEVAL_MIN_SCORE: float = 0.35
    RERANK_ENABLED: bool = True
    # monoPTT5-3B (Unicamp): reranker treinado para português. Pede GPU ou bastante RAM.
    RERANK_MODEL: str = "unicamp-dl/monoptt5-3b"
    # Chunks maiores (~600 tokens) com overlap ~20% — melhor para livros didáticos.
    CHUNK_CHILD_TOKENS: int = 600
    CHUNK_OVERLAP_TOKENS: int = 120

    # LangSmith (RF31)
    LANGCHAIN_TRACING_V2: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "deepedu-dev"

    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    CHROMA_DIR: str = "./data/chroma"
    MATERIALS_DIR: str = "./data/materials"
    CHAT_DB_PATH: str = "./data/chat_history/chat_history.db"
    BILLING_DB_PATH: str = "./data/billing/billing.db"
    AUDIT_DB_PATH: str = "./data/audit/audit.db"
    AUDIT_PHONE_SALT: str = ""
    AUDIT_FAIL_CLOSED: bool = True
    PHONE_ENCRYPTION_KEY: str = ""
    CONSENT_TERMS_VERSION: str = "1.0"
    CONSENT_SCHOOL_NAME: str = "sua escola"
    MESSAGE_DEDUP_TTL_HOURS: int = 48

    BILLING_ENFORCE_SUBSCRIPTION: bool = False
    BILLING_TRIAL_DAYS: int = 7
    BILLING_PLAN_DAYS: int = 30
    BILLING_CURRENCY: str = "BRL"
    SCHOOL_PLAN_DAYS: int = 30
    SCHOOL_PLAN_AMOUNT: float = 499.00

    ASAAS_API_KEY: str = ""
    ASAAS_BASE_URL: str = "https://api.asaas.com/v3"
    ASAAS_WEBHOOK_TOKEN: str = ""
    ASAAS_BILLING_AMOUNT: float = 29.90
    ASAAS_DEFAULT_BILLING_TYPE: str = "UNDEFINED"

    ADMIN_API_KEY: str = ""


settings = Settings()
