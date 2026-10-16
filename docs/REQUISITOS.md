# Especificação de Requisitos — RAG de Matemática (Ensino Médio)

> **Implementação em vigor (13/10/2026).** A pergunta da tese é se este pipeline pode ser auditado. O RAG é o objeto auditado. O LLM que roda é `amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct` (0,49B), não o Qwen2.5-Math 1.5B citado nos requisitos antigos abaixo. O orçamento operacional continua perto de 4.000 tokens para caber em notebook modesto; a janela nativa desse modelo é 32.768.

| Campo | Valor |
|-------|-------|
| **Projeto** | DeepEdu — Tutor RAG de Matemática para Ensino Médio |
| **Versão do documento** | 1.2 |
| **Data** | 29/06/2026 |
| **Status** | Aprovado para desenvolvimento |
| **Público-alvo** | Estudantes do Ensino Médio (15–17 anos), via WhatsApp |

---

## 1. Introdução

### 1.1 Propósito

Este documento define os requisitos funcionais (RF) e não funcionais (RNF) para um sistema RAG modular de tutoria em Matemática do Ensino Médio brasileiro, com canal principal WhatsApp, painel web de controle e execução em servidor Linux local (Ubuntu) via containers Docker.

### 1.2 Escopo

**Incluído:**
- Pipeline completo de ingestão, indexação, recuperação e geração
- Chatbot pedagógico com memória de conversa
- Integração WhatsApp Business Cloud API
- Dashboard web administrativo
- Conformidade com BNCC (Matemática EM), LGPD e ECA Digital (Lei 15.211/2025)
- Auditoria via LangSmith

**Excluído (fase inicial):**
- Fine-tuning de modelos
- App mobile nativo
- Correção automática de redações longas
- Integração com LMS específico (Moodle, Google Classroom etc.)

### 1.3 Definições e siglas

| Termo | Definição |
|-------|-----------|
| **BNCC** | Base Nacional Comum Curricular — documento normativo do MEC |
| **EM13MAT** | Código de habilidade de Matemática no Ensino Médio (ex.: EM13MAT101) |
| **ECA Digital** | Lei 15.211/2025 — Estatuto Digital da Criança e do Adolescente |
| **TIR** | Tool-integrated Reasoning — raciocínio com ferramenta externa (ex.: SymPy) |
| **RAG** | Retrieval-Augmented Generation |
| **Chunk** | Fragmento de texto indexado no banco vetorial |
| **Parent-document retrieval** | Recuperação por chunk pequeno com contexto expandido do documento pai |

### 1.4 Referências normativas

- [BNCC Ensino Médio — MEC](https://www.gov.br/mec/pt-br/cne/bncc-2013-ensino-medio)
- [BNCC Matemática EM — PDF oficial](https://www.gov.br/mec/pt-br/cne/bncc_ensino_medio.pdf)
- Lei 13.709/2018 (LGPD)
- Lei 15.211/2025 (ECA Digital)
- [WhatsApp Cloud API — Meta](https://developers.facebook.com/docs/whatsapp/cloud-api/)
- [LangChain / LangGraph](https://python.langchain.com/)
- [LangSmith](https://docs.smith.langchain.com/)

---

## 2. Arquitetura de referência

### 2.1 Módulos do sistema

| ID | Módulo | Responsabilidade |
|----|--------|------------------|
| **M01** | Channel Adapters | WhatsApp, chat web de teste |
| **M02** | Orquestrador (LangGraph) | Fluxo RAG, agente, ferramentas |
| **M03** | Serviço de Memória | Histórico por sessão, resumo |
| **M04** | Retriever Híbrido | BM25 + denso + re-ranking |
| **M05** | Gerador (LLM + TIR) | Qwen2.5-Math + SymPy |
| **M06** | Pipeline de Ingestão | Loaders, limpeza, chunking, OCR |
| **M07** | Banco Vetorial | Chroma (teste) / Qdrant (produção) |
| **M08** | Metadados BNCC | PostgreSQL ou equivalente |
| **M09** | Governança | LangSmith, auditoria, LGPD |
| **M10** | Dashboard Web | Controle, métricas, gestão de corpus |

### 2.2 Contratos de interface (modularidade — RNF09)

Cada módulo expõe interface substituível:

```
IngestionProvider      → carrega e normaliza documentos
VectorStoreProvider    → indexa e consulta vetores (Chroma/Qdrant)
RetrieverProvider      → retrieval denso/esparsa/híbrida
LLMProvider            → geração e TIR
ChannelAdapter         → entrada/saída por canal (WhatsApp, Web)
MemoryStore            → persistência de sessão
```

### 2.3 Fases de entrega

| Fase | Escopo | Critério de conclusão |
|------|--------|----------------------|
| **F1 — MVP local** | Ingestão, RAG, chat web, LangSmith | 10 perguntas de referência respondidas com citação |
| **F2 — WhatsApp piloto** | Webhook, fila, memória, consentimento | Mensagem real processada end-to-end |
| **F3 — Produção escolar** | Qdrant, dashboard, BNCC, ECA Digital | Checklist de conformidade 100% nos itens obrigatórios |

---

## 3. Requisitos funcionais

### RF01 — Chatbot pedagógico coloquial

**Descrição:** O sistema deve responder consultas em linguagem coloquial e acessível a adolescentes (15–17 anos), mantendo rigor matemático.

**Módulos:** M02, M05, M01

**Critérios de aceitação:**
- [ ] Respostas em português brasileiro, tom de tutor (não robótico)
- [ ] Evita jargão não explicado; define termos na primeira ocorrência
- [ ] Em 90% de um conjunto de 20 perguntas piloto, avaliadores classificam tom como "adequado ao EM"

---

### RF02 — Configuração do ecossistema LangChain

**Descrição:** Utilizar LangChain como base de composição de componentes (loaders, retrievers, chains/runnables).

**Módulos:** M02, M04, M05, M06

**Critérios de aceitação:**
- [ ] Dependências LangChain versionadas em `requirements.txt` ou equivalente
- [ ] Componentes compostos via LCEL (`|` pipe) onde aplicável
- [ ] Documentação de versões mínimas no README do projeto

---

### RF03 — Memória de conversa multi-turno

**Descrição:** Manter contexto entre mensagens da mesma sessão para conversas com múltiplas trocas.

**Módulos:** M03, M02

**Critérios de aceitação:**
- [ ] Sessão identificada por `session_id` (WhatsApp: número + thread; Web: UUID)
- [ ] Pergunta de follow-up ("e no caso da função quadrática?") usa histórico sem repetir contexto inteiro
- [ ] Memória persiste entre reinícios do container (volume ou banco)

---

### RF04 — Orquestração com LangGraph

**Descrição:** Orquestrar o fluxo conversacional com LangGraph e checkpointer (substitui `ConversationChain`, depreciado).

**Módulos:** M02

**Critérios de aceitação:**
- [ ] Grafo definido com nós: `retrieve` → `generate` → (opcional) `verify` → `respond`
- [ ] Checkpointer configurado (SQLite, PostgreSQL ou Redis)
- [ ] Suporte a `stream` e `ainvoke` para respostas assíncronas
- [ ] Não utiliza `ConversationChain` em código de produção

---

### RF05 — Interface web de chat (teste e admin)

**Descrição:** Interface web simples para interação com o chatbot e testes internos.

**Módulos:** M01, M10

**Critérios de aceitação:**
- [ ] Campo de entrada de mensagem e histórico visível
- [ ] Exibe fontes citadas (RF29)
- [ ] Acessível apenas com autenticação (RNF14)
- [ ] Renderiza fórmulas LaTeX via MathJax ou KaTeX (RF34)

---

### RF06 — Prompts personalizados para Matemática EM

**Descrição:** Prompts de sistema versionados para tutoria em Matemática do Ensino Médio.

**Módulos:** M02, M05

**Critérios de aceitação:**
- [ ] Arquivo(s) de prompt em `prompts/` com versionamento (ex.: `v1_tutor_em.md`)
- [ ] Prompt inclui: persona de tutor, idioma PT-BR, pedido de passos, proibição de inventar fontes
- [ ] Prompt distingue modo tutor (padrão) e modo avaliação (RF44)
- [ ] Alteração de prompt não exige mudança de código (apenas config/arquivo)
- [ ] **Prompt de sistema ≤ 400 tokens** (tokenizer Qwen2.5-Math) — ver `docs/TOKEN_BUDGET.md`
- [ ] Prompt instrui respostas concisas (economia de tokens para janela 4K)

---

### RF07 — Consciência de contexto em conversas

**Descrição:** Utilizar histórico, intenção e entidades para respostas contextualizadas.

**Módulos:** M02, M03

**Critérios de aceitação:**
- [ ] Referência a mensagens anteriores da sessão em respostas coerentes
- [ ] Extração de entidades matemáticas (tema, função, equação) registrada no estado do grafo
- [ ] Teste: sequência de 3 mensagens sobre o mesmo problema mantém coerência

---

### RF08 — Gestão otimizada de memória

**Descrição:** Combinar memória de buffer e resumo; limitar detalhes desnecessários.

**Módulos:** M03

**Critérios de aceitação:**
- [ ] Janela de buffer configurável (padrão: últimas 4 trocas)
- [ ] Resumo automático quando histórico excede **600 tokens** (`HISTORY_SUMMARY_TRIGGER`)
- [ ] Histórico (buffer + resumo) **≤ 800 tokens** no prompt final
- [ ] Resumo preserva: tema matemático, dados do problema, passos já explicados
- [ ] Entrada incompleta ou ambígua gera pergunta de esclarecimento (não resposta inventada)
- [ ] Contagem de tokens com tokenizer Qwen (não estimativa por caracteres)

---

### RF09 — Decomposição de consultas e ferramentas externas

**Descrição:** Decompor consultas complexas em subtarefas; usar ferramentas (APIs, calculadora, SymPy).

**Módulos:** M02, M05

**Critérios de aceitação:**
- [ ] Agente com nó `plan` para perguntas multi-etapa (ex.: "explique e calcule a derivada de x²+3x")
- [ ] Ferramenta `sympy_calculate` disponível ao agente
- [ ] Ferramenta `search_knowledge_base` disponível ao agente
- [ ] Resultados das ferramentas integrados na resposta final (RF10)

---

### RF10 — Síntese coerente de respostas

**Descrição:** Integrar resultados de retrieval e ferramentas numa resposta única e coerente.

**Módulos:** M02, M05

**Critérios de aceitação:**
- [ ] Resposta final não expõe JSON interno ou logs de ferramentas
- [ ] Estrutura pedagógica: contexto → passos → conclusão
- [ ] Sem contradição entre trechos recuperados e cálculo via SymPy

---

### RF11 — Armazenamento e atualização dinâmica de contexto

**Descrição:** Armazenar entradas, intenções e entidades; atualizar com novas mensagens.

**Módulos:** M03, M02

**Critérios de aceitação:**
- [ ] Estado da sessão inclui: `messages`, `intent`, `entities`, `bncc_tags` (quando identificados)
- [ ] Nova mensagem atualiza estado antes da geração
- [ ] Contexto recuperado do RAG é separado do histórico conversacional

---

### RF12 — Arquitetura RAG (componentes obrigatórios)

**Descrição:** O sistema deve implementar Retriever, Gerador, Fonte de conhecimento e Orquestrador.

**Módulos:** M04, M05, M06, M07, M02

**Critérios de aceitação:**
- [ ] Cada componente em módulo/pacote separado com interface definida
- [ ] Orquestrador conecta retriever → gerador em fluxo contínuo
- [ ] Fonte de conhecimento consultável independentemente do canal (WhatsApp/Web)

---

### RF13 — Recuperação híbrida (denso + esparso)

**Descrição:** Combinar busca densa (embeddings) e esparsa (BM25) com fusão de resultados.

**Módulos:** M04

**Critérios de aceitação:**
- [ ] Implementação BM25 (ex.: `rank_bm25` ou índice OpenSearch/Elasticsearch)
- [ ] Implementação densa via banco vetorial (M07)
- [ ] Fusão por Reciprocal Rank Fusion (RRF) ou equivalente documentado
- [ ] Parâmetro `top_k` configurável por ambiente
- [ ] Em benchmark interno de 30 perguntas, híbrido ≥ denso isolado em precisão@5

---

### RF14 — Gerador com modelo de domínio matemático

**Descrição:** Utilizar modelo especializado em matemática, não LLM genérico.

**Módulos:** M05

**Critérios de aceitação:**
- [ ] Modelo: `Qwen2.5-Math-1.5B-Instruct` (ou versão superior aprovada)
- [ ] Janela de contexto: **4.096 tokens** (`max_position_embeddings` — série Math, não 128K)
- [ ] Inferência local via Ollama, vLLM ou transformers
- [ ] `LLM_MAX_NEW_TOKENS=1024`, `LLM_TEMPERATURE=0.3` (documentado em `.env.example`)
- [ ] Montagem de prompt respeita orçamento em `docs/TOKEN_BUDGET.md`
- [ ] Fallback documentado se modelo indisponível (degradação graceful)

---

### RF15 — Fontes de conhecimento estruturadas e não estruturadas

**Descrição:** Suportar PDFs, DOCX, TXT e fontes estruturadas com metadados.

**Módulos:** M06, M07, M08

**Critérios de aceitação:**
- [ ] Loaders: PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader (ou equivalente)
- [ ] Fonte estruturada: tabela/arquivo com mapeamento BNCC (CSV, JSON ou PostgreSQL)
- [ ] Cada documento indexado com metadados mínimos (RF36)
- [ ] Web em tempo real **não** é fonte primária; apenas whitelist opcional (RF19)

---

### RF16 — Pipeline de ingestão em lote

**Descrição:** Carregar e processar documentos em lotes para evitar esgotamento de memória.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] Parâmetro `batch_size` configurável (padrão: 32–64 documentos)
- [ ] Script CLI `run_indexing.py` (ou equivalente) processa diretório inteiro
- [ ] Log de progresso: documentos processados / total / erros
- [ ] Falha em um documento não interrompe o lote inteiro

---

### RF17 — Limpeza e normalização de texto

**Descrição:** Remover ruído, normalizar texto e eliminar duplicados antes da indexação.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] Remoção de tags HTML, caracteres de controle, headers/footers repetitivos de PDF
- [ ] Normalização de espaços e quebras de linha
- [ ] Detecção de duplicados por hash de conteúdo (SHA-256)
- [ ] Relatório pós-ingestão: docs inseridos, ignorados, duplicados

---

### RF18 — Tratamento multi-formato de documentos

**Descrição:** Suportar texto, PDF nativo, DOCX; OCR para PDFs escaneados.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] PDF com texto selecionável: extração via PyPDFLoader ou pdfplumber
- [ ] PDF escaneado: OCR via Tesseract ou docTR com flag `--ocr`
- [ ] DOCX: extração de parágrafos e tabelas
- [ ] Formatos não suportados geram log de aviso, não crash

---

### RF19 — Web controlada (opcional)

**Descrição:** Permitir ingestão web apenas de domínios na whitelist, com revisão.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] Lista de domínios permitidos em configuração
- [ ] WebBaseLoader desabilitado por padrão
- [ ] Conteúdo web passa pelas mesmas etapas de limpeza (RF17) antes de indexar

---

### RF20 — Fragmentação (chunking) semântica

**Descrição:** Segmentar por frases e parágrafos, preservando blocos matemáticos.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] Separadores: `\n\n`, `. `, com exceção para blocos LaTeX (`$...$`, `$$...$$`)
- [ ] Chunk não corta equação ao meio
- [ ] Estratégia documentada no README técnico

---

### RF21 — Chunks granulares com parent-document retrieval

**Descrição:** Chunks pequenos para busca precisa; contexto expandido do documento pai na geração.

**Módulos:** M04, M06

**Critérios de aceitação:**
- [ ] Tamanho alvo do chunk filho: 300–400 tokens (configurável)
- [ ] Chunk injetado no prompt (parent truncado): **máx. 400 tokens** cada
- [ ] Total de contexto RAG no prompt: **máx. 1.200 tokens** (`top_k=3` padrão)
- [ ] Retriever retorna chunk filho; gerador recebe parent truncado ao orçamento
- [ ] Truncagem por fim de parágrafo, nunca no meio de equação

---

### RF22 — Geração de embeddings

**Descrição:** Incorporar texto com modelo multilíngue compatível com português.

**Módulos:** M06, M07

**Critérios de aceitação:**
- [ ] Modelo padrão: `intfloat/multilingual-e5-base` (Hugging Face) ou equivalente aprovado
- [ ] Alternativa OpenAI documentada em configuração
- [ ] Dimensão do vetor registrada nos metadados do índice
- [ ] Embeddings gerados em lote (RF23)

---

### RF23 — Embeddings em lote

**Descrição:** Processar embeddings em batch para eficiência em grande escala.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] `embedding_batch_size` configurável (padrão: 64)
- [ ] Tempo de indexação de 1000 chunks documentado em benchmark interno

---

### RF24 — Banco de dados vetorial

**Descrição:** Armazenar e consultar vetores com ambientes distintos para teste e produção.

**Módulos:** M07

**Critérios de aceitação:**
- [ ] Testes/desenvolvimento: **Chroma** (embutido ou client-server)
- [ ] Produção: **Qdrant** (ou pgvector se PostgreSQL já existir — decisão documentada em ADR)
- [ ] Troca de provider via configuração, sem alterar lógica de negócio (RNF09)
- [ ] Coleção/index com nome e versão (ex.: `matematica_em_v1`)

---

### RF25 — Similaridade por cosseno

**Descrição:** Usar similaridade cosseno na busca densa.

**Módulos:** M04, M07

**Critérios de aceitação:**
- [ ] Métrica configurada como `cosine` no banco vetorial
- [ ] Score de similaridade retornado e registrado no LangSmith

---

### RF26 — Re-ranking pós-recuperação

**Descrição:** Aplicar re-ranking para melhorar precisão após fusão híbrida.

**Módulos:** M04

**Critérios de aceitação:**
- [ ] Cross-encoder ou LLM-reranker aplicado aos top-N candidatos (N ≥ 20, retorno top 5)
- [ ] Re-ranking configurável (on/off) por ambiente
- [ ] Latência adicional documentada (p95)

---

### RF27 — Filtragem de conteúdo sensível na indexação

**Descrição:** Detectar e mascarar dados confidenciais antes da indexação.

**Módulos:** M06, M09

**Critérios de aceitação:**
- [ ] Regex/heurísticas para: CPF, e-mail, telefone, "senha", "cartão"
- [ ] Substituição por `[REDACTED]` antes de persistir
- [ ] Log de redações sem expor valor original

---

### RF28 — Mitigação de viés

**Descrição:** Reduzir respostas tendenciosas ou estereotipadas.

**Módulos:** M02, M05

**Critérios de aceitação:**
- [ ] Prompt instrui inclusão de perspectivas diversas quando aplicável
- [ ] Corpus de indexação documentado quanto à diversidade de fontes
- [ ] Revisão manual trimestral de 20 respostas aleatórias (procedimento documentado)

---

### RF29 — Transparência: citação de fontes

**Descrição:** Apresentar documentos/chunks usados na geração da resposta.

**Módulos:** M02, M01, M10

**Critérios de aceitação:**
- [ ] Cada resposta inclui: `documento`, `página` (se disponível), `chunk_id`, `habilidade_bncc` (se mapeada)
- [ ] WhatsApp: citação em texto compacto (ex.: "Fonte: Apostila Funções, p.12")
- [ ] Web: citação com link para visualização do chunk no dashboard
- [ ] Resposta sem chunk recuperado aciona RF38 (abstinência)

---

### RF30 — Privacidade e conformidade LGPD

**Descrição:** Anonimização, auditoria, consentimento e direitos do titular.

**Módulos:** M09

**Critérios de aceitação:**
- [ ] PII removida/mascarada antes de indexação (RF27)
- [ ] Registro de auditoria: `timestamp`, `session_id` pseudonimizado, `action`, `resource`
- [ ] Endpoint/procedimento para exclusão de dados da sessão por solicitação
- [ ] Política de retenção configurável (padrão: 90 dias para histórico de chat)
- [ ] ROPA (registro de operações de tratamento) documentado em `docs/ROPA.md`

---

### RF31 — Auditoria via LangSmith

**Descrição:** Rastrear todas as execuções do pipeline RAG no LangSmith.

**Módulos:** M09, M02

**Critérios de aceitação:**
- [ ] `LANGCHAIN_TRACING_V2=true` em produção
- [ ] Tags por execução: `session_id`, `channel`, `bncc_skill` (quando aplicável)
- [ ] Traces incluem: query, chunks recuperados, scores, prompt, resposta, latência
- [ ] Projeto LangSmith separado por ambiente (dev/staging/prod)

---

### RF32 — Conformidade ECA Digital (Lei 15.211/2025)

**Descrição:** Atender obrigações para sistemas com acesso provável por menores.

**Módulos:** M09, M01

**Critérios de aceitação:**
- [ ] Inventário do ecossistema digital documentado (`docs/ECA_DIGITAL_CHECKLIST.md`)
- [ ] Arquitetura de auditoria implementada conforme `docs/AUDITORIA_ECA.md`
- [ ] Consentimento parental granular, não genérico (RF42)
- [ ] Verificação de faixa etária sem autodeclaração simples (vínculo com matrícula ou código escolar)
- [ ] DPIA (Relatório de Impacto) preenchido antes de produção
- [ ] Cláusulas contratuais com escola: exclusão de dados, notificação de incidentes em 24h
- [ ] Proibição de uso de dados de alunos para publicidade ou perfilamento
- [ ] **Todo módulo** (M01–M10) emite eventos auditáveis (RF47)

---

### RF33 — Alinhamento BNCC — Matemática Ensino Médio

**Descrição:** Respostas e conteúdo indexado alinhados às competências e habilidades EM13MAT.

**Módulos:** M08, M02, M05

**Critérios de aceitação:**
- [ ] Base normativa: documento oficial MEC (não apenas plataformas auxiliares)
- [ ] Metadados incluem código de habilidade quando identificável (ex.: EM13MAT305)
- [ ] Resposta referencia competência/habilidade quando pertinente
- [ ] Catálogo de habilidades carregado em M08 a partir do PDF/CSV oficial
- [ ] bncc.digital pode ser fonte auxiliar de planos, não norma legal

---

### RF34 — Notação matemática (LaTeX)

**Descrição:** Suportar fórmulas e símbolos matemáticos na geração e exibição.

**Módulos:** M05, M01, M10

**Critérios de aceitação:**
- [ ] LLM gera fórmulas em LaTeX inline (`$...$`) e display (`$$...$$`)
- [ ] Dashboard renderiza com MathJax ou KaTeX
- [ ] WhatsApp: fallback para notação linear legível (ex.: `x^2 + 3x`) quando LaTeX não renderiza
- [ ] Opcional: gerar imagem da fórmula para WhatsApp (fase F3)

---

### RF35 — Verificação de respostas (TIR com SymPy)

**Descrição:** Validar cálculos numéricos e simbólicos com ferramenta externa.

**Módulos:** M05, M02

**Critérios de aceitação:**
- [ ] Ferramenta SymPy integrada ao agente (RF09)
- [ ] Respostas com resultado numérico passam por verificação antes de envio
- [ ] Divergência LLM vs SymPy: priorizar SymPy e sinalizar correção ao usuário
- [ ] Log de verificações no LangSmith

---

### RF36 — Metadados por documento

**Descrição:** Cada documento indexado deve ter metadados estruturados.

**Módulos:** M06, M08

**Critérios de aceitação:**
- [ ] Campos obrigatórios: `titulo`, `fonte`, `tipo` (apostila, exercício, BNCC)
- [ ] Campos opcionais: `serie` (1/2/3 EM), `tema`, `habilidade_bncc`, `autor`, `ano_letivo`
- [ ] Metadados consultáveis como filtro no retriever (ex.: `serie=2`)

---

### RF37 — Política de abstinência

**Descrição:** Não responder quando confiança ou recuperação forem insuficientes.

**Módulos:** M02, M04

**Critérios de aceitação:**
- [ ] Se max score de retrieval < limiar configurável: resposta padrão "Não encontrei material suficiente..."
- [ ] Sem citação de fonte → não afirmar fatos do corpus
- [ ] Mensagem sugere reformular pergunta ou consultar professor
- [ ] Taxa de abstinência monitorada no dashboard (RNF12)

---

### RF38 — Avaliação contínua da qualidade RAG

**Descrição:** Conjunto de testes de regressão para qualidade de recuperação e geração.

**Módulos:** M09, M10

**Critérios de aceitação:**
- [ ] Dataset de ≥ 50 perguntas com resposta esperada e fonte esperada
- [ ] Métricas: precision@5, faithfulness, citation_accuracy
- [ ] Script `scripts/eval_rag.py` executável em CI
- [ ] Regressão > 5% em qualquer métrica bloqueia deploy (RNF15)

---

### RF39 — Reindexação incremental e versionamento

**Descrição:** Atualizar índice sem reprocessar corpus inteiro; versionar coleções.

**Módulos:** M06, M07

**Critérios de aceitação:**
- [ ] Adicionar/remover documento sem reindexação completa
- [ ] Nova versão de coleção (ex.: `v2`) criável em paralelo; switch por configuração
- [ ] Rollback para versão anterior em < 5 minutos

---

### RF40 — Integração WhatsApp Cloud API

**Descrição:** Comunicação com clientes via WhatsApp Business Cloud API (Meta).

**Módulos:** M01

**Critérios de aceitação:**
- [ ] Webhook HTTPS público com verificação `hub.challenge`
- [ ] Validação de assinatura `X-Hub-Signature-256`
- [ ] Resposta HTTP 200 em < 1s; processamento assíncrono via fila (Redis/RQ, Celery ou equivalente)
- [ ] Envio de resposta via Graph API com `phone_number_id` e token de sistema
- [ ] Suporte a janela de 24h e templates para mensagens fora da janela
- [ ] Documentação de setup em `docs/WHATSAPP.md`

---

### RF41 — Idempotência de mensagens WhatsApp

**Descrição:** Evitar processamento duplicado de webhooks.

**Módulos:** M01

**Critérios de aceitação:**
- [ ] `message_id` persistido com TTL ≥ 48h
- [ ] Segundo webhook com mesmo `message_id` retorna 200 sem reprocessar
- [ ] Teste automatizado simula retry da Meta

---

### RF42 — Consentimento e opt-out

**Descrição:** Fluxo de consentimento LGPD/ECA Digital e cancelamento.

**Módulos:** M01, M09

**Critérios de aceitação:**
- [ ] Primeira interação: mensagem de termos + opção de aceitar/recusar
- [ ] Comando `SAIR` ou equivalente: interrompe processamento e marca opt-out
- [ ] Registro de consentimento: `timestamp`, `phone_hash`, `version_termos`
- [ ] Sem consentimento: apenas mensagem informativa, sem RAG

---

### RF43 — Modos pedagógicos (tutor vs avaliação)

**Descrição:** Diferenciar explicação passo a passo de entrega direta de gabarito.

**Módulos:** M02, M06

**Critérios de aceitação:**
- [ ] Modo tutor (padrão): scaffolding, pistas, não entrega resposta final de prova
- [ ] Modo avaliação: ativado por flag admin; apenas referência a material, sem resolver lista
- [ ] Detecção heurística de "me dá a resposta da prova" → recusa educada

---

### RF44 — Dashboard web de controle

**Descrição:** Painel para gestão do sistema RAG sem sobrecarregar o servidor.

**Módulos:** M10

**Critérios de aceitação:**
- [ ] Telas: status dos serviços, métricas (latência, abstinência, mensagens/dia)
- [ ] Gestão de corpus: upload, listagem, reindexação
- [ ] Visualização de chunks e metadados BNCC
- [ ] Acesso a traces LangSmith (link externo ou embed)
- [ ] RBAC: admin, operador, somente leitura (RNF14)

---

### RF45 — Tratamento de tabelas e imagens em PDFs

**Descrição:** Preservar estrutura de tabelas e descrição de figuras para RAG.

**Módulos:** M06

**Critérios de aceitação:**
- [ ] Tabelas extraídas como Markdown ou CSV embutido no chunk
- [ ] Imagens/figuras: descrição textual ou alt-text quando OCR/disponível
- [ ] Teste com ≥ 3 PDFs contendo tabelas de exercícios

---

### RF46 — Orçamento de tokens para Qwen2.5-Math (4K)

**Descrição:** Toda montagem de prompt, memória e retrieval deve respeitar a janela de **4.096 tokens** do `Qwen2.5-Math-1.5B-Instruct`.

**Módulos:** M02, M03, M04, M05

**Critérios de aceitação:**
- [ ] Documento `docs/TOKEN_BUDGET.md` implementado no código
- [ ] Contagem com tokenizer Qwen (`AutoTokenizer` do modelo)
- [ ] Orçamento padrão: sistema 400 + RAG 1.200 + histórico 800 + usuário 400 + geração 1.024
- [ ] Truncagem em ordem de prioridade (RAG → histórico → usuário) conforme TOKEN_BUDGET
- [ ] LangSmith registra `input_tokens`, `rag_tokens`, `history_tokens`, `output_tokens`
- [ ] Teste TB-01 a TB-05 de `docs/TOKEN_BUDGET.md` passando em CI
- [ ] Não usar `VLLM_ALLOW_LONG_MAX_MODEL_LEN` em produção

---

### RF47 — Sistema integralmente auditável (ECA Digital + LGPD)

**Descrição:** Todo o projeto deve ser auditável de ponta a ponta: canais, pipeline RAG, administração, consentimento e incidentes. A auditoria é obrigatória por força do ECA Digital (Lei 15.211/2025) e da LGPD, não opcional.

**Módulos:** M01–M10, M09 (camada transversal)

**Critérios de aceitação:**
- [ ] Arquitetura documentada em `docs/AUDITORIA_ECA.md`
- [ ] Tabela `audit_log` append-only com schema definido (event_id, correlation_id, actor, action, outcome, metadata)
- [ ] Tabela `consent_log` imutável para aceite/recusa de termos
- [ ] **Fail-closed:** se gravação de log falhar, não processar mensagem de menor
- [ ] LangSmith (RF31) como camada técnica complementar — **não substitui** log local
- [ ] Todos os eventos obrigatórios da seção 5 de AUDITORIA_ECA implementados
- [ ] Script `scripts/export_audit.py` para relatórios da escola/DPO
- [ ] Testes AU-01 a AU-07 passando
- [ ] Retenção: audit_log 12 meses; consent_log 5 anos
- [ ] Dashboard: tela de consulta de logs (papel admin/DPO, RBAC R13)

---

## 4. Requisitos não funcionais

### RNF01 — Stack LangChain, LangGraph e LangSmith

**Critérios de aceitação:**
- [ ] LangGraph para orquestração de agentes
- [ ] LangSmith para tracing em todos os ambientes não locais
- [ ] Versões fixadas e testadas em conjunto

---

### RNF02 — Bancos vetoriais por ambiente

| Ambiente | Banco |
|----------|-------|
| Desenvolvimento / testes | Chroma |
| Produção | Qdrant (padrão) ou pgvector (se ADR aprovar) |

**Critérios de aceitação:**
- [ ] Variável `VECTOR_STORE_PROVIDER` seleciona implementação
- [ ] Testes de integração rodam contra Chroma em CI

---

### RNF03 — Sistema operacional

**Critérios de aceitação:**
- [ ] Ubuntu Server 22.04 LTS ou 24.04 LTS
- [ ] Documentação de instalação testada em Ubuntu limpo

---

### RNF04 — API WhatsApp

**Critérios de aceitação:**
- [ ] WhatsApp Business Cloud API (Meta) como canal oficial
- [ ] Twilio ou BSP alternativo permitido se compatível com Cloud API
- [ ] Domínio com TLS válido para webhook

---

### RNF05 — Engenharia de prompt

**Critérios de aceitação:**
- [ ] Prompts versionados em arquivos, não hardcoded
- [ ] Revisão de prompt exige PR e teste de regressão (RF38)

---

### RNF06 — Interface web leve

**Critérios de aceitação:**
- [ ] Frontend estático ou SSR leve (FastAPI + Jinja, ou SPA mínima)
- [ ] Não exige GPU no cliente
- [ ] Tempo de carregamento inicial < 3s em rede local

---

### RNF07 — Containerização Docker modular

**Critérios de aceitação:**
- [ ] `docker-compose.yml` com serviços: `api`, `worker`, `qdrant`, `redis`, `dashboard` (opcional)
- [ ] Cada serviço com Dockerfile próprio
- [ ] Volumes para dados persistentes (índice, uploads, memória)
- [ ] Healthcheck em cada container

---

### RNF08 — Arquitetura reutilizável (base para outros RAGs)

**Critérios de aceitação:**
- [ ] Troca de domínio (ex.: Física) alterando: corpus, prompts, metadados — sem reescrever core
- [ ] Interfaces `Protocol` ou ABC documentadas em `app/core/interfaces/`

---

### RNF09 — Modelo LLM

**Critérios de aceitação:**
- [ ] `Qwen2.5-Math-1.5B-Instruct` como padrão
- [ ] Contexto máximo: **4.096 tokens** (série Math; não confundir com Qwen2.5 genérico 128K)
- [ ] Requisito mínimo de hardware documentado: 8 GB RAM (CPU) ou 6 GB VRAM (GPU)
- [ ] Variável `LLM_MODEL` para override em testes
- [ ] Variáveis de orçamento em `.env.example`: `RAG_CONTEXT_MAX_TOKENS`, `HISTORY_MAX_TOKENS`, `LLM_MAX_NEW_TOKENS`

---

### RNF10 — Idioma

**Critérios de aceitação:**
- [ ] Português brasileiro como idioma principal de interface e respostas
- [ ] Embeddings multilíngues compatíveis com PT

---

### RNF11 — Desempenho

**Critérios de aceitação:**
- [ ] p95 latência end-to-end WhatsApp (mensagem recebida → resposta enviada) < 30s em hardware de referência
- [ ] p95 retrieval < 2s
- [ ] p95 geração LLM < 20s (1.5B, CPU aceitável com aviso)

---

### RNF12 — Observabilidade

**Critérios de aceitação:**
- [ ] Logs estruturados (JSON) com `correlation_id`
- [ ] Métricas Prometheus ou equivalente: `rag_latency`, `retrieval_score`, `abstention_rate`
- [ ] Alertas configuráveis para erro > 5% em 5 minutos

---

### RNF13 — Segurança

**Critérios de aceitação:**
- [ ] Segredos em variáveis de ambiente ou vault, nunca em código
- [ ] `ADMIN_API_KEY` ou OAuth para endpoints administrativos
- [ ] Rate limit por IP e por número WhatsApp
- [ ] HTTPS obrigatório em produção

---

### RNF14 — Controle de acesso (RBAC)

**Critérios de aceitação:**
- [ ] Papéis: `admin`, `operator`, `viewer`
- [ ] Matriz de permissões documentada em `docs/RBAC.md`

---

### RNF15 — CI/CD e qualidade

**Critérios de aceitação:**
- [ ] Pipeline CI: lint, testes unitários, `eval_rag.py` em dataset reduzido
- [ ] Regressão de métricas RAG bloqueia merge na branch principal
- [ ] Build de imagens Docker em cada release tag

---

### RNF16 — Backup e recuperação

**Critérios de aceitação:**
- [ ] Backup diário: banco vetorial, metadados, corpus em `data/materials`
- [ ] Procedimento de restore documentado e testado trimestralmente
- [ ] RPO ≤ 24h; RTO ≤ 4h

---

### RNF17 — Escalabilidade horizontal (fase F3)

**Critérios de aceitação:**
- [ ] Workers de fila escaláveis (`docker compose up --scale worker=3`)
- [ ] API stateless; estado em banco/fila

---

---

## 5. Matriz de rastreabilidade

### 5.1 RF → Módulo → Fase → Teste

| RF | Módulo(s) | Fase | ID Teste |
|----|-----------|------|----------|
| RF01 | M02, M05, M01 | F1 | T-01 |
| RF02 | M02, M04, M05, M06 | F1 | T-02 |
| RF03 | M03, M02 | F1 | T-03 |
| RF04 | M02 | F1 | T-04 |
| RF05 | M01, M10 | F1 | T-05 |
| RF06 | M02, M05 | F1 | T-06 |
| RF07 | M02, M03 | F1 | T-07 |
| RF08 | M03 | F1 | T-08 |
| RF09 | M02, M05 | F1 | T-09 |
| RF10 | M02, M05 | F1 | T-10 |
| RF11 | M03, M02 | F1 | T-11 |
| RF12 | M02–M07 | F1 | T-12 |
| RF13 | M04 | F1 | T-13 |
| RF14 | M05 | F1 | T-14 |
| RF15 | M06, M07, M08 | F1 | T-15 |
| RF16 | M06 | F1 | T-16 |
| RF17 | M06 | F1 | T-17 |
| RF18 | M06 | F1 | T-18 |
| RF19 | M06 | F3 | T-19 |
| RF20 | M06 | F1 | T-20 |
| RF21 | M04, M06 | F1 | T-21 |
| RF22 | M06, M07 | F1 | T-22 |
| RF23 | M06 | F1 | T-23 |
| RF24 | M07 | F1/F3 | T-24 |
| RF25 | M04, M07 | F1 | T-25 |
| RF26 | M04 | F2 | T-26 |
| RF27 | M06, M09 | F2 | T-27 |
| RF28 | M02, M05 | F3 | T-28 |
| RF29 | M02, M01, M10 | F1 | T-29 |
| RF30 | M09 | F2 | T-30 |
| RF31 | M09, M02 | F1 | T-31 |
| RF32 | M09, M01 | F3 | T-32 |
| RF33 | M08, M02, M05 | F3 | T-33 |
| RF34 | M05, M01, M10 | F1 | T-34 |
| RF35 | M05, M02 | F1 | T-35 |
| RF36 | M06, M08 | F1 | T-36 |
| RF37 | M02, M04 | F1 | T-37 |
| RF38 | M09, M10 | F2 | T-38 |
| RF39 | M06, M07 | F2 | T-39 |
| RF40 | M01 | F2 | T-40 |
| RF41 | M01 | F2 | T-41 |
| RF42 | M01, M09 | F2 | T-42 |
| RF43 | M02, M06 | F2 | T-43 |
| RF44 | M10 | F2/F3 | T-44 |
| RF45 | M06 | F2 | T-45 |
| RF46 | M02, M03, M04, M05 | F1 | T-46 |
| RF47 | M01–M10, M09 | F2/F3 | T-47 |

### 5.2 RNF → Módulo → Verificação

| RNF | Módulo(s) | Verificação |
|-----|-----------|-------------|
| RNF01 | M02, M09 | Inspeção de dependências + trace LangSmith |
| RNF02 | M07 | Teste integração Chroma (CI) + Qdrant (staging) |
| RNF03 | Infra | Instalação Ubuntu limpa |
| RNF04 | M01 | Webhook Meta verificado |
| RNF05 | M02, M05 | PR review + eval |
| RNF06 | M10 | Lighthouse / tempo de carga |
| RNF07 | Infra | `docker compose up` completo |
| RNF08 | Core | Troca de domínio em spike |
| RNF09 | M05 | Benchmark latência |
| RNF10 | Todos | Revisão de conteúdo PT |
| RNF11 | Todos | Teste de carga k6 ou locust |
| RNF12 | M09, M10 | Dashboard Grafana/Prometheus |
| RNF13 | M01, M10 | Pentest básico / OWASP ZAP |
| RNF14 | M10 | Matriz RBAC |
| RNF15 | CI | Pipeline verde |
| RNF16 | Infra | Drill de restore |
| RNF17 | Infra | Scale workers |

### 5.3 Mapeamento requisitos originais → novos

| Original | Novo | Observação |
|----------|------|------------|
| RF1 | RF01 | Tom pedagógico EM |
| RF2 | RF02 | Mantido |
| RF3 | RF03 | Mantido |
| RF4 | RF04 | LangGraph substitui ConversationChain |
| RF5 | RF05 | Mantido |
| RF6 | RF06 | Escopo matemática EM |
| RF7 | RF07 | Mantido |
| RF8 | RF08 | Mantido |
| RF9 | RF09 | Mantido |
| RF10 | RF10 | Mantido |
| RF11 | RF11 | Mantido |
| RF13 | RF12 | Renumeração |
| RF14 | RF13 | Híbrido unificado |
| RF15 | RF14 | Modelo de domínio, não fine-tune obrigatório |
| RF16 | RF15 | Mantido |
| RF17 | RF12 | Integrado ao orquestrador |
| RF19 | RF16 | Mantido |
| RF20 | RF17 | Mantido |
| RF21 (duplicado) | RF18, RF19 | Separado multi-formato vs web |
| RF21 chunking | RF20 | Preservação LaTeX |
| RF22 | RF21 | Parent-document |
| RF23 | RF22 | Mantido |
| RF24 | RF23 | Mantido |
| RF25 | RF24 | Chroma + Qdrant definido |
| RF26 | RF25 | Mantido |
| RF27 | RF13 | Unificado |
| RF28 | RF27 | Mantido |
| RF29 | RF28 | Mantido |
| RF30 | RF29 | Mantido |
| RF31 | RF30 | LGPD operacional |
| RF32 | RF31 | Mantido |
| RF33 | RF32 | ECA Digital como checklist |
| RF34 | RF33 | BNCC operacional |
| RNF1–RNF10 | RNF01–RNF17 | Expandido e detalhado |
| — | RF34–RF45 | Novos (matemática, WhatsApp, avaliação) |
| — | RNF11–RNF17 | Novos (perf, segurança, backup) |

---

## 6. Plano de testes de aceitação (resumo)

| ID | Descrição | RF/RNF | Tipo |
|----|-----------|--------|------|
| T-01 | 20 perguntas piloto — avaliação de tom | RF01 | Manual |
| T-04 | Grafo LangGraph executa sem ConversationChain | RF04 | Automatizado |
| T-13 | Benchmark híbrido vs denso (30 perguntas) | RF13 | Automatizado |
| T-14 | Qwen2.5-Math-1.5B-Instruct responde equação | RF14 | Automatizado |
| T-29 | Resposta inclui citação com página | RF29 | Automatizado |
| T-35 | SymPy corrige divergência de cálculo | RF35 | Automatizado |
| T-37 | Score baixo → mensagem de abstinência | RF37 | Automatizado |
| T-38 | `eval_rag.py` — precision@5 ≥ 0.7 | RF38 | CI |
| T-40 | Webhook Meta end-to-end em staging | RF40 | Integração |
| T-41 | Retry duplicado não gera segunda resposta | RF41 | Automatizado |
| T-42 | Sem consentimento → sem RAG | RF42 | Integração |
| T-32 | Checklist ECA Digital 100% itens obrigatórios | RF32 | Manual |
| T-33 | Resposta cita EM13MAT quando aplicável | RF33 | Manual |
| T-46 | Entrada do prompt ≤ 2.900 tokens; geração ≤ 1.024 | RF46 | Automatizado |
| T-47 | Mensagem menor gera audit_log + LangSmith; fail-closed se log falhar | RF47 | Integração |
| AU-01 a AU-07 | Bateria de auditoria ECA | RF47 | Ver `AUDITORIA_ECA.md` |

---

## 7. Glossário de habilidades BNCC (referência)

O sistema deve suportar as **5 competências específicas** de Matemática no EM:

1. Utilizar estratégias e conceitos para interpretar e resolver problemas
2. Analisar relações entre grandezas para modelagem matemática
3. Investigar e produzir conjecturas com linguagem matemática
4. Compreender e utilizar diferentes registros de representação
5. Investigar e estabelecer conjecturas com abordagem formal

Códigos de habilidade seguem o padrão `EM13MATnnn` (ex.: EM13MAT101). O catálogo completo deve ser importado do documento oficial MEC para M08.

---

## 8. Aprovações

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| Product Owner | | | |
| Tech Lead | | | |
| Responsável pedagógico | | | |
| DPO / Privacidade | | | |

---

## 9. Histórico de revisões

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 29/06/2026 | DeepEdu | Versão inicial revisada a partir da análise de requisitos |
| 1.1 | 29/06/2026 | DeepEdu | Orçamento de tokens Qwen2.5-Math 4K (RF46, TOKEN_BUDGET, prompts) |
| 1.2 | 29/06/2026 | DeepEdu | RF47 auditoria integral ECA; docs/AUDITORIA_ECA.md |
