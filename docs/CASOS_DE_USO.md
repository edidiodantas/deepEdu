# Casos de Uso — DeepEdu (derivados de RF e RNF)

| Campo | Valor |
|-------|-------|
| **Versão** | 1.0 |
| **Projeto** | DeepEdu — Tutor RAG Matemática EM |
| **Base** | `docs/REQUISITOS.md` v1.2 |
| **Formato** | Um caso de uso por RF/RNF |

---

## 1. Visão geral

Cada caso de uso (UC) rastreia diretamente um requisito funcional (RF) ou não funcional (RNF).
Atores principais: **Estudante EM**, **Administrador/DPO**, **Operador**, **Sistema DeepEdu**.

### Diagrama de contexto

```
Estudante ──WhatsApp──► DeepEdu API ──► RAG (retrieval + Qwen + SymPy)
                              │
Administrador ──painel/API──►├─► audit_log / LangSmith
DPO ──export────────────────┘
```

---

## 2. Casos de uso funcionais (RF)

### UC-RF01 — Chatbot pedagógico coloquial

| Campo | Valor |
|-------|-------|
| **Requisito** | RF01 |
| **Módulos** | M02, M05, M01 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** O sistema deve responder consultas em linguagem coloquial e acessível a adolescentes (15–17 anos), mantendo rigor matemático. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Chatbot pedagógico coloquial».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF01.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF02 — Configuração do ecossistema LangChain

| Campo | Valor |
|-------|-------|
| **Requisito** | RF02 |
| **Módulos** | M02, M04, M05, M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Utilizar LangChain como base de composição de componentes (loaders, retrievers, chains/runnables). |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Configuração do ecossistema LangChain».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF02.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF03 — Memória de conversa multi-turno

| Campo | Valor |
|-------|-------|
| **Requisito** | RF03 |
| **Módulos** | M03, M02 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Manter contexto entre mensagens da mesma sessão para conversas com múltiplas trocas. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Memória de conversa multi-turno».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF03.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF04 — Orquestração com LangGraph

| Campo | Valor |
|-------|-------|
| **Requisito** | RF04 |
| **Módulos** | M02 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Orquestrar o fluxo conversacional com LangGraph e checkpointer (substitui `ConversationChain`, depreciado). |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Orquestração com LangGraph».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF04.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF05 — Interface web de chat (teste e admin)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF05 |
| **Módulos** | M01, M10 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Interface web simples para interação com o chatbot e testes internos. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Interface web de chat (teste e admin)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF05.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF06 — Prompts personalizados para Matemática EM

| Campo | Valor |
|-------|-------|
| **Requisito** | RF06 |
| **Módulos** | M02, M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Prompts de sistema versionados para tutoria em Matemática do Ensino Médio. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Prompts personalizados para Matemática EM».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF06.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF07 — Consciência de contexto em conversas

| Campo | Valor |
|-------|-------|
| **Requisito** | RF07 |
| **Módulos** | M02, M03 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Utilizar histórico, intenção e entidades para respostas contextualizadas. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Consciência de contexto em conversas».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF07.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF08 — Gestão otimizada de memória

| Campo | Valor |
|-------|-------|
| **Requisito** | RF08 |
| **Módulos** | M03 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Combinar memória de buffer e resumo; limitar detalhes desnecessários. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Gestão otimizada de memória».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF08.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF09 — Decomposição de consultas e ferramentas externas

| Campo | Valor |
|-------|-------|
| **Requisito** | RF09 |
| **Módulos** | M02, M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Decompor consultas complexas em subtarefas; usar ferramentas (APIs, calculadora, SymPy). |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Decomposição de consultas e ferramentas externas».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF09.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF10 — Síntese coerente de respostas

| Campo | Valor |
|-------|-------|
| **Requisito** | RF10 |
| **Módulos** | M02, M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Integrar resultados de retrieval e ferramentas numa resposta única e coerente. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Síntese coerente de respostas».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF10.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF11 — Armazenamento e atualização dinâmica de contexto

| Campo | Valor |
|-------|-------|
| **Requisito** | RF11 |
| **Módulos** | M03, M02 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Armazenar entradas, intenções e entidades; atualizar com novas mensagens. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Armazenamento e atualização dinâmica de contexto».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF11.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF12 — Arquitetura RAG (componentes obrigatórios)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF12 |
| **Módulos** | M04, M05, M06, M07, M02 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** O sistema deve implementar Retriever, Gerador, Fonte de conhecimento e Orquestrador. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Arquitetura RAG (componentes obrigatórios)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF12.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF13 — Recuperação híbrida (denso + esparso)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF13 |
| **Módulos** | M04 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Combinar busca densa (embeddings) e esparsa (BM25) com fusão de resultados. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Recuperação híbrida (denso + esparso)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF13.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF14 — Gerador com modelo de domínio matemático

| Campo | Valor |
|-------|-------|
| **Requisito** | RF14 |
| **Módulos** | M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Utilizar modelo especializado em matemática, não LLM genérico. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Gerador com modelo de domínio matemático».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF14.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF15 — Fontes de conhecimento estruturadas e não estruturadas

| Campo | Valor |
|-------|-------|
| **Requisito** | RF15 |
| **Módulos** | M06, M07, M08 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Suportar PDFs, DOCX, TXT e fontes estruturadas com metadados. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Fontes de conhecimento estruturadas e não estruturadas».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF15.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF16 — Pipeline de ingestão em lote

| Campo | Valor |
|-------|-------|
| **Requisito** | RF16 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Carregar e processar documentos em lotes para evitar esgotamento de memória. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Pipeline de ingestão em lote».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF16.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF17 — Limpeza e normalização de texto

| Campo | Valor |
|-------|-------|
| **Requisito** | RF17 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Remover ruído, normalizar texto e eliminar duplicados antes da indexação. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Limpeza e normalização de texto».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF17.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF18 — Tratamento multi-formato de documentos

| Campo | Valor |
|-------|-------|
| **Requisito** | RF18 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Suportar texto, PDF nativo, DOCX; OCR para PDFs escaneados. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Tratamento multi-formato de documentos».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF18.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF19 — Web controlada (opcional)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF19 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Permitir ingestão web apenas de domínios na whitelist, com revisão. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Web controlada (opcional)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF19.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF20 — Fragmentação (chunking) semântica

| Campo | Valor |
|-------|-------|
| **Requisito** | RF20 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Segmentar por frases e parágrafos, preservando blocos matemáticos. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Fragmentação (chunking) semântica».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF20.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF21 — Chunks granulares com parent-document retrieval

| Campo | Valor |
|-------|-------|
| **Requisito** | RF21 |
| **Módulos** | M04, M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Chunks pequenos para busca precisa; contexto expandido do documento pai na geração. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Chunks granulares com parent-document retrieval».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF21.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF22 — Geração de embeddings

| Campo | Valor |
|-------|-------|
| **Requisito** | RF22 |
| **Módulos** | M06, M07 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Incorporar texto com modelo multilíngue compatível com português. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Geração de embeddings».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF22.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF23 — Embeddings em lote

| Campo | Valor |
|-------|-------|
| **Requisito** | RF23 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Processar embeddings em batch para eficiência em grande escala. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Embeddings em lote».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF23.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF24 — Banco de dados vetorial

| Campo | Valor |
|-------|-------|
| **Requisito** | RF24 |
| **Módulos** | M07 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Armazenar e consultar vetores com ambientes distintos para teste e produção. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Banco de dados vetorial».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF24.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF25 — Similaridade por cosseno

| Campo | Valor |
|-------|-------|
| **Requisito** | RF25 |
| **Módulos** | M04, M07 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Usar similaridade cosseno na busca densa. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Similaridade por cosseno».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF25.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF26 — Re-ranking pós-recuperação

| Campo | Valor |
|-------|-------|
| **Requisito** | RF26 |
| **Módulos** | M04 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Aplicar re-ranking para melhorar precisão após fusão híbrida. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Re-ranking pós-recuperação».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF26.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF27 — Filtragem de conteúdo sensível na indexação

| Campo | Valor |
|-------|-------|
| **Requisito** | RF27 |
| **Módulos** | M06, M09 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Detectar e mascarar dados confidenciais antes da indexação. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Filtragem de conteúdo sensível na indexação».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF27.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF28 — Mitigação de viés

| Campo | Valor |
|-------|-------|
| **Requisito** | RF28 |
| **Módulos** | M02, M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Reduzir respostas tendenciosas ou estereotipadas. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Mitigação de viés».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF28.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF29 — Transparência: citação de fontes

| Campo | Valor |
|-------|-------|
| **Requisito** | RF29 |
| **Módulos** | M02, M01, M10 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Apresentar documentos/chunks usados na geração da resposta. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Transparência: citação de fontes».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF29.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF30 — Privacidade e conformidade LGPD

| Campo | Valor |
|-------|-------|
| **Requisito** | RF30 |
| **Módulos** | M09 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Anonimização, auditoria, consentimento e direitos do titular. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Privacidade e conformidade LGPD».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF30.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF31 — Auditoria via LangSmith

| Campo | Valor |
|-------|-------|
| **Requisito** | RF31 |
| **Módulos** | M09, M02 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Rastrear todas as execuções do pipeline RAG no LangSmith. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Auditoria via LangSmith».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF31.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF32 — Conformidade ECA Digital (Lei 15.211/2025)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF32 |
| **Módulos** | M09, M01 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Atender obrigações para sistemas com acesso provável por menores. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Conformidade ECA Digital (Lei 15.211/2025)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF32.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF33 — Alinhamento BNCC — Matemática Ensino Médio

| Campo | Valor |
|-------|-------|
| **Requisito** | RF33 |
| **Módulos** | M08, M02, M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Respostas e conteúdo indexado alinhados às competências e habilidades EM13MAT. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Alinhamento BNCC — Matemática Ensino Médio».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF33.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF34 — Notação matemática (LaTeX)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF34 |
| **Módulos** | M05, M01, M10 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Suportar fórmulas e símbolos matemáticos na geração e exibição. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Notação matemática (LaTeX)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF34.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF35 — Verificação de respostas (TIR com SymPy)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF35 |
| **Módulos** | M05, M02 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Validar cálculos numéricos e simbólicos com ferramenta externa. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Verificação de respostas (TIR com SymPy)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF35.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF36 — Metadados por documento

| Campo | Valor |
|-------|-------|
| **Requisito** | RF36 |
| **Módulos** | M06, M08 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Cada documento indexado deve ter metadados estruturados. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Metadados por documento».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF36.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF37 — Política de abstinência

| Campo | Valor |
|-------|-------|
| **Requisito** | RF37 |
| **Módulos** | M02, M04 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Não responder quando confiança ou recuperação forem insuficientes. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Política de abstinência».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF37.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF38 — Avaliação contínua da qualidade RAG

| Campo | Valor |
|-------|-------|
| **Requisito** | RF38 |
| **Módulos** | M09, M10 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Conjunto de testes de regressão para qualidade de recuperação e geração. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Avaliação contínua da qualidade RAG».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF38.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF39 — Reindexação incremental e versionamento

| Campo | Valor |
|-------|-------|
| **Requisito** | RF39 |
| **Módulos** | M06, M07 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Atualizar índice sem reprocessar corpus inteiro; versionar coleções. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Reindexação incremental e versionamento».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF39.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF40 — Integração WhatsApp Cloud API

| Campo | Valor |
|-------|-------|
| **Requisito** | RF40 |
| **Módulos** | M01 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Comunicação com clientes via WhatsApp Business Cloud API (Meta). |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Integração WhatsApp Cloud API».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF40.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF41 — Idempotência de mensagens WhatsApp

| Campo | Valor |
|-------|-------|
| **Requisito** | RF41 |
| **Módulos** | M01 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Evitar processamento duplicado de webhooks. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Idempotência de mensagens WhatsApp».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF41.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF42 — Consentimento e opt-out

| Campo | Valor |
|-------|-------|
| **Requisito** | RF42 |
| **Módulos** | M01, M09 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Fluxo de consentimento LGPD/ECA Digital e cancelamento. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Consentimento e opt-out».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF42.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF43 — Modos pedagógicos (tutor vs avaliação)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF43 |
| **Módulos** | M02, M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Diferenciar explicação passo a passo de entrega direta de gabarito. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Modos pedagógicos (tutor vs avaliação)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF43.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF44 — Dashboard web de controle

| Campo | Valor |
|-------|-------|
| **Requisito** | RF44 |
| **Módulos** | M10 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Painel para gestão do sistema RAG sem sobrecarregar o servidor. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Dashboard web de controle».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF44.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF45 — Tratamento de tabelas e imagens em PDFs

| Campo | Valor |
|-------|-------|
| **Requisito** | RF45 |
| **Módulos** | M06 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Preservar estrutura de tabelas e descrição de figuras para RAG. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Tratamento de tabelas e imagens em PDFs».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF45.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF46 — Orçamento de tokens para Qwen2.5-Math (4K)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF46 |
| **Módulos** | M02, M03, M04, M05 |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Toda montagem de prompt, memória e retrieval deve respeitar a janela de **4.096 tokens** do `Qwen2.5-Math-1.5B-Instruct`. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Orçamento de tokens para Qwen2.5-Math (4K)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF46.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

### UC-RF47 — Sistema integralmente auditável (ECA Digital + LGPD)

| Campo | Valor |
|-------|-------|
| **Requisito** | RF47 |
| **Módulos** | M01–M10, M09 (camada transversal) |
| **Atores** | Estudante EM, Sistema DeepEdu |
| **Pré-condições** | Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado. |
| **Descrição** | **Descrição:** Todo o projeto deve ser auditável de ponta a ponta: canais, pipeline RAG, administração, consentimento e incidentes. A auditoria é obrigatória por força do ECA Digital (Lei 15.211/2025) e da LGPD, não opcional. |

**Fluxo principal:**

1. Estudante EM envia ação relacionada a «Sistema integralmente auditável (ECA Digital + LGPD)».
2. Sistema valida matrícula, consentimento e auditoria (fail-closed).
3. Sistema executa pipeline necessário para RF47.
4. Sistema registra eventos (`audit_log` / LangSmith).
5. Sistema retorna resultado ao ator ou operador.

| **Pós-condições** | Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel. |

---

## 3. Casos de uso não funcionais (RNF)

### UC-RNF01 — Stack LangChain, LangGraph e LangSmith

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF01 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] LangGraph para orquestração de agentes - [ ] LangSmith para tracing em todos os ambientes não locais - [ ] Versões fixadas e testadas em conjunto |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF01 — Stack LangChain, LangGraph e LangSmith.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF02 — Bancos vetoriais por ambiente

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF02 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | | Ambiente | Banco | |----------|-------| | Desenvolvimento / testes | Chroma | | Produção | Qdrant (padrão) ou pgvector (se ADR aprovar) | |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF02 — Bancos vetoriais por ambiente.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF03 — Sistema operacional

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF03 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Ubuntu Server 22.04 LTS ou 24.04 LTS - [ ] Documentação de instalação testada em Ubuntu limpo |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF03 — Sistema operacional.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF04 — API WhatsApp

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF04 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] WhatsApp Business Cloud API (Meta) como canal oficial - [ ] Twilio ou BSP alternativo permitido se compatível com Cloud API - [ ] Domínio com TLS válido para webhook |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF04 — API WhatsApp.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF05 — Engenharia de prompt

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF05 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Prompts versionados em arquivos, não hardcoded - [ ] Revisão de prompt exige PR e teste de regressão (RF38) |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF05 — Engenharia de prompt.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF06 — Interface web leve

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF06 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Frontend estático ou SSR leve (FastAPI + Jinja, ou SPA mínima) - [ ] Não exige GPU no cliente - [ ] Tempo de carregamento inicial < 3s em rede local |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF06 — Interface web leve.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF07 — Containerização Docker modular

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF07 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] `docker-compose.yml` com serviços: `api`, `worker`, `qdrant`, `redis`, `dashboard` (opcional) - [ ] Cada serviço com Dockerfile próprio - [ ] Volumes para dados persistentes (índice, uploads, memória) - [ ] Healthche |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF07 — Containerização Docker modular.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF08 — Arquitetura reutilizável (base para outros RAGs)

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF08 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Troca de domínio (ex.: Física) alterando: corpus, prompts, metadados — sem reescrever core - [ ] Interfaces `Protocol` ou ABC documentadas em `app/core/interfaces/` |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF08 — Arquitetura reutilizável (base para outros RAGs).
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF09 — Modelo LLM

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF09 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] `Qwen2.5-Math-1.5B-Instruct` como padrão - [ ] Contexto máximo: **4.096 tokens** (série Math; não confundir com Qwen2.5 genérico 128K) - [ ] Requisito mínimo de hardware documentado: 8 GB RAM (CPU) ou 6 GB VRAM (GPU) |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF09 — Modelo LLM.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF10 — Idioma

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF10 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Português brasileiro como idioma principal de interface e respostas - [ ] Embeddings multilíngues compatíveis com PT |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF10 — Idioma.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF11 — Desempenho

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF11 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] p95 latência end-to-end WhatsApp (mensagem recebida → resposta enviada) < 30s em hardware de referência - [ ] p95 retrieval < 2s - [ ] p95 geração LLM < 20s (1.5B, CPU aceitável com aviso) |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF11 — Desempenho.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF12 — Observabilidade

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF12 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Logs estruturados (JSON) com `correlation_id` - [ ] Métricas Prometheus ou equivalente: `rag_latency`, `retrieval_score`, `abstention_rate` - [ ] Alertas configuráveis para erro > 5% em 5 minutos |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF12 — Observabilidade.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF13 — Segurança

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF13 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Segredos em variáveis de ambiente ou vault, nunca em código - [ ] `ADMIN_API_KEY` ou OAuth para endpoints administrativos - [ ] Rate limit por IP e por número WhatsApp - [ ] HTTPS obrigatório em produção |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF13 — Segurança.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF14 — Controle de acesso (RBAC)

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF14 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Papéis: `admin`, `operator`, `viewer` - [ ] Matriz de permissões documentada em `docs/RBAC.md` |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF14 — Controle de acesso (RBAC).
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF15 — CI/CD e qualidade

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF15 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Pipeline CI: lint, testes unitários, `eval_rag.py` em dataset reduzido - [ ] Regressão de métricas RAG bloqueia merge na branch principal - [ ] Build de imagens Docker em cada release tag |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF15 — CI/CD e qualidade.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF16 — Backup e recuperação

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF16 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Backup diário: banco vetorial, metadados, corpus em `data/materials` - [ ] Procedimento de restore documentado e testado trimestralmente - [ ] RPO ≤ 24h; RTO ≤ 4h |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF16 — Backup e recuperação.
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

### UC-RNF17 — Escalabilidade horizontal (fase F3)

| Campo | Valor |
|-------|-------|
| **Requisito** | RNF17 |
| **Módulos** | — |
| **Atores** | Sistema DeepEdu, Operador, DPO |
| **Pré-condições** | Ambiente configurado conforme `.env.example` e documentação de deploy. |
| **Descrição** | **Critérios de aceitação:** - [ ] Workers de fila escaláveis (`docker compose up --scale worker=3`) - [ ] API stateless; estado em banco/fila |

**Fluxo de verificação:**

1. Operador/DPO inicia verificação de RNF17 — Escalabilidade horizontal (fase F3).
2. Sistema aplica configuração, limites ou política correspondente.
3. Métricas, logs ou testes automatizados confirmam conformidade.
4. Evidência arquivada (relatório eval, backup, CI).

| **Pós-condições** | Critério de aceitação do requisito verificado em teste ou checklist. |

---

## 4. Matriz de rastreabilidade UC → RF/RNF

| UC | Requisito | Tipo |
|----|-----------|------|
| UC-RF1 | RF01 | RF |
| UC-RF2 | RF02 | RF |
| UC-RF3 | RF03 | RF |
| UC-RF4 | RF04 | RF |
| UC-RF5 | RF05 | RF |
| UC-RF6 | RF06 | RF |
| UC-RF7 | RF07 | RF |
| UC-RF8 | RF08 | RF |
| UC-RF9 | RF09 | RF |
| UC-RF0 | RF10 | RF |
| UC-RF1 | RF11 | RF |
| UC-RF2 | RF12 | RF |
| UC-RF3 | RF13 | RF |
| UC-RF4 | RF14 | RF |
| UC-RF5 | RF15 | RF |
| UC-RF6 | RF16 | RF |
| UC-RF7 | RF17 | RF |
| UC-RF8 | RF18 | RF |
| UC-RF9 | RF19 | RF |
| UC-RF0 | RF20 | RF |
| UC-RF1 | RF21 | RF |
| UC-RF2 | RF22 | RF |
| UC-RF3 | RF23 | RF |
| UC-RF4 | RF24 | RF |
| UC-RF5 | RF25 | RF |
| UC-RF6 | RF26 | RF |
| UC-RF7 | RF27 | RF |
| UC-RF8 | RF28 | RF |
| UC-RF9 | RF29 | RF |
| UC-RF0 | RF30 | RF |
| UC-RF1 | RF31 | RF |
| UC-RF2 | RF32 | RF |
| UC-RF3 | RF33 | RF |
| UC-RF4 | RF34 | RF |
| UC-RF5 | RF35 | RF |
| UC-RF6 | RF36 | RF |
| UC-RF7 | RF37 | RF |
| UC-RF8 | RF38 | RF |
| UC-RF9 | RF39 | RF |
| UC-RF0 | RF40 | RF |
| UC-RF1 | RF41 | RF |
| UC-RF2 | RF42 | RF |
| UC-RF3 | RF43 | RF |
| UC-RF4 | RF44 | RF |
| UC-RF5 | RF45 | RF |
| UC-RF6 | RF46 | RF |
| UC-RF7 | RF47 | RF |
| UC-RNF01 | RNF01 | RNF |
| UC-RNF02 | RNF02 | RNF |
| UC-RNF03 | RNF03 | RNF |
| UC-RNF04 | RNF04 | RNF |
| UC-RNF05 | RNF05 | RNF |
| UC-RNF06 | RNF06 | RNF |
| UC-RNF07 | RNF07 | RNF |
| UC-RNF08 | RNF08 | RNF |
| UC-RNF09 | RNF09 | RNF |
| UC-RNF10 | RNF10 | RNF |
| UC-RNF11 | RNF11 | RNF |
| UC-RNF12 | RNF12 | RNF |
| UC-RNF13 | RNF13 | RNF |
| UC-RNF14 | RNF14 | RNF |
| UC-RNF15 | RNF15 | RNF |
| UC-RNF16 | RNF16 | RNF |
| UC-RNF17 | RNF17 | RNF |
