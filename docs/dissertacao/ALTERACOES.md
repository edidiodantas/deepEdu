# Alterações na dissertação — revisão de 1º nov. 2026

Arquivo de origem: Dissertacao_final (1).docx. Arquivo revisado: Dissertacao_DeepEdu_revisada.docx (e o PDF correspondente).
Os 39 trechos de código do Apêndice A não foram alterados e continuam idênticos ao repositório (commit 6d67901 / main 447364e).

## Revisão de 5 nov. 2026 (8ª rodada): verificação final para impressão

Foi feita uma verificação completa da versão de qualificação. As correções também foram aplicadas à versão 5nov.

Itens conferidos:
1. **Citações e referências.** As 55 referências estão em ordem alfabética. Toda referência é citada no texto, e toda citação tem referência, com o ano igual.
2. **Sumário e listas de figuras e quadros.** As 72 entradas conferem com as páginas do PDF: 95 páginas na versão de qualificação e 97 na 5nov.
3. **Apêndice A comparado com o repositório** (main 7ef29a2, 5 nov. 2026). Os 39 trechos de código com indicação de fonte são idênticos às linhas indicadas. Os 4 blocos de parâmetros (chunking, recuperação, LLM e orçamento de tokens) conferem com .env.local.example e app/core/config.py.
4. **Restos de marcações.** Não há [data], destaques, "XXX" nem espaços ou pontuação duplicados no texto. Os "[...]" que restam são os da ABNT nas referências de eventos. CIDADE, ANO e "Mestre em área" foram mantidos por decisão do autor.
5. **Ortografia.** Foi feita uma verificação automática do texto em português. Não apareceram erros, só termos técnicos e palavras estrangeiras.
6. **Termos absolutos e juízos de valor do próprio autor.** Foram suavizados:
   - "três fatores cruciais" passou a "três fatores";
   - "mediar essa convergência de forma eficaz, ética e transparente (LEWIS; FINARDI)" passou a "contribuir para essa convergência ao fundamentar as respostas em uma base de conhecimento identificável (LEWIS)";
   - "aplicações inovadoras" passou a "aplicações";
   - "comprometer significativamente" passou a "comprometer";
   - "evoluiu significativamente" passou a "evoluiu";
   - "implementação robusta" passou a "implementação";
   - quatro ocorrências de "particularmente relevante" foram reescritas;
   - "cenário promissor" passou a "indica um cenário";
   - "amplamente adotada" passou a "adotada";
   - "um número significativo de pesquisas" passou a "pesquisas";
   - na frase sobre o PLUTO, "demonstrou alta precisão" passou a "obteve nota máxima em 93,33%".
7. **Itálico em termos estrangeiros.** Foi aplicado em 18 ocorrências que estavam sem itálico: chatbot, prompt, embedding, framework, websites, benchmarks, retriever, chunks, fail-closed, pipeline, apud e caput. Nomes de arquivos e de eventos do código não foram alterados.

## Revisão de 5 nov. 2026 (7ª rodada): Fonseca conferido com o PDF

O PDF enviado é o TCC (em formato de artigo) de Pedro Luiz Monnerat Fonseca, Rafael da Silva Costa e Flávio Luiz Seixas, do Bacharelado em Sistemas de Informação da UFF, aprovado em 27/06/2025. Tudo o que a seção 5.6 diz confere com o texto:
- a Lina;
- o WhatsApp;
- o LlamaIndex, o Qdrant e o gpt-4o-mini;
- a avaliação com uma médica endocrinologista: qualidade da recuperação, precisão factual e ausência de riscos.

Na referência, "Graduação em Sistemas de Informação" passou a "Bacharelado em Sistemas de Informação". Foram atualizadas as duas versões: a da qualificação e a 5nov.

## Revisão de 5 nov. 2026 (6ª rodada): Silvestre conferido com o PDF

O PDF enviado pelo autor confirma os números da seção 5.8: 2.434 documentos, 35 comparações e 34 alunos. Ele confirma também o resultado (compreensão e coerência das respostas). Alterações:
- a frase da seção 5.8 passou a dizer que a base tem 2.434 documentos PDF e 667 páginas web, segundo a seção 3.1 do TCC, e que as comparações foram avaliadas com o RAGAS;
- pela ficha catalográfica do trabalho, a entrada é "Schweizer Silvestre, Ana Sofia". A citação passou a "Schweizer Silvestre (2025)" e a referência a SCHWEIZER SILVESTRE, A. S., agora com 52 p., "Monografia (Bacharelado em Ciência da Computação)", link e data de acesso. A referência foi movida para depois de SCHOLARAI.
As duas versões foram atualizadas: qualificação, com 95 p., e 5nov, com 97 p. O sumário foi conferido nas duas.

## Revisão de 5 nov. 2026 (5ª rodada): versão para a qualificação

A pedido do autor, foi gerado o Dissertacao_DeepEdu_qualificacao.docx/.pdf (95 páginas) a partir da versão da 4ª rodada:
- foram retiradas a página da ficha catalográfica e a folha de aprovação;
- saiu "Acesso em: [data]" das referências de BRASIL (Lei 15.211, BNCC, CNE/CEB), CARLOS e FONSECA, que deve voltar na versão de defesa;
- os destaques amarelos foram retirados;
- sumário e listas foram atualizados e conferidos com o PDF (72 entradas).
CIDADE, ANO e "Mestre em área" foram mantidos, por decisão do autor.

## Revisão de 5 nov. 2026 (4ª rodada): revisão final para impressão

1. BOSTROM; YUDKOWSKY: as páginas p. 316-334 foram confirmadas e mantidas.
2. JOHNSON; DOUZE; JÉGOU: v. 7, n. 3, p. 535-547, 2019, confirmados. Foi acrescentado o DOI 10.1109/TBDATA.2019.2921572.
3. Data de acesso "5 nov. 2026" em CEIA-UFG e SOARES et al., que antes tinham "[data]", e em KAPA e SCHOLARAI, que antes tinham 27 nov. 2024 e 2 jun. 2025. Os quatro links foram abertos e conferidos nesse dia, e as frases correspondentes foram reescritas com base nessa consulta.
4. Conferência cruzada: as 55 referências estão em ordem alfabética, cada uma é citada no texto e cada citação tem referência.
5. Sumário e listas de figuras e quadros conferidos com o PDF: 72 entradas, todas corretas. O documento tem 97 páginas.
6. Apêndice A: os trechos de código não foram alterados nesta revisão. Continuam como na conferência com o repositório (commit 6d67901 / main 447364e). A única mudança no apêndice foi tirar uma citação de uma frase do A.5 (2ª rodada).

O que ainda depende do autor está em PENDENCIAS.md.

## Revisão de 5 nov. 2026 (3ª rodada): Orrenius e Bartczak retirados

A pedido do autor, que não conseguiu baixar os originais, ORRENIUS (2024) e BARTCZAK (2024) foram retirados do texto e das referências. Na seção 5.8, a lista de trabalhos citados por Araújo passou a ter Maj et al. e Chiras. A frase com os resultados dos dois passou a ser atribuída só a Araújo: "A revisão de Araújo (2025) relata ganho de até 8,5% na precisão das consultas SQL com RAG, mas também o aumento do custo computacional e a necessidade de otimizar o contexto recuperado." O documento passou a ter 97 páginas. O sumário e as listas de figuras e quadros foram atualizados e conferidos com o PDF (72 entradas).

## Revisão de 5 nov. 2026 (2ª rodada): conferência das obras na internet

Arquivo atualizado: Dissertacao_DeepEdu_revisada_5nov.docx (e .pdf), que substitui a versão da 1ª rodada. São 98 páginas. No sumário, 5.6 passou para a p. 36 e 5.7 para a p. 37. Cada frase foi reescrita só com o que a obra citada diz.

Texto:
1. Introdução: Brown et al. e Touvron et al. passaram a sustentar só o avanço dos LLMs, e não aplicações educacionais.
2. Seção 4.1: a memória paramétrica e a não paramétrica passaram a ser atribuídas a Lewis et al. (2020), no lugar de Karpukhin. Lang e Gürpinar saíram da frase sobre precisão, atualização e transparência, ficando só Gao et al. A tríade de componentes passou de Finardi et al. para Lewis et al. Na frase sobre esparsa, densa e híbrida, Karpukhin ficou para a abordagem híbrida, e Johnson et al. (FAISS) para a busca densa. A frase sobre Nouali et al. agora informa que o estudo usou BM25 e que o rag-llama foi melhor na maioria das métricas. O texto dizia antes que o estudo comparava abordagens densas e esparsas. A frase sobre o modelo generativo passou de Brown/Touvron para Lewis et al.
3. Seção 4.2: a frase de Gao et al. sobre aplicações educacionais foi substituída pela revisão de Yahaya et al. (factualidade, desempenho e explicabilidade). A citação de Thesen e Park saiu da "base inspecionável", que o artigo não menciona. "alcançam precisão superior" passou a "podem alcançar". Taneja et al. passou a sustentar só a privacidade da implantação local.
4. Seção 4.3: a citação de Finardi saiu da frase sobre sanitização de documentos, que agora apresenta "medidas de mitigação possíveis". A frase sobre RAGAS em Borges foi ajustada: o RAGAS avaliou o conjunto de dados sintético.
5. Seções 5.1 a 5.7:
   - Taneja et al. (privacidade).
   - Pampel et al. ("alguma familiaridade técnica"; Flowise; PDF).
   - Touvron et al. (liberação do LLaMA à comunidade de pesquisa).
   - Miladi et al.: 17% contra 10%, p = 0,017, SUS 80,4. Saiu a frase dos "menos de 2 segundos", que não existe no artigo.
   - Seção 5.5: retiradas as citações de Brown e Touvron sobre o ajuste por proficiência, apresentado agora como possibilidade.
   - NeuroBot: retirada a frase do limiar configurável; "confiaram muito mais"; "143 respondentes".
   - RAGent: "94,4% responderam 'sim' ou 'talvez'"; "limites dinâmicos" passou a "limiares".
6. Seção 5.8:
   - "Taschetto e Fileto (2024)", com o resultado 3-shot em Matemática e Ciências da Natureza.
   - "Ferreira (2025)", autor único, Câmpus São João da Boa Vista, com os ganhos em pontos percentuais (16%→61% e 63%→95%).
   - Borges (RAGAS no conjunto sintético).
   - "Cherubini et al. (2024)".
   - ScholarAI ("milhões de artigos revisados por pares"). Saíram os "200 milhões" e as limitações, que não têm fonte.
   - Kapa: retirados CircleCI e Mapbox.
   - **Loures (2025) retirado do texto e das referências**, a pedido do autor.
7. Seção 5.9:
   - A abertura foi reescrita: saíram "injeção de conhecimento", "forte potencial" e a citação de Finardi.
   - RAG-HAT: "redução de cerca de 27%". Saiu "custo computacional elevado".
8. Seção 6.1:
   - A frase dos chunks de 256 a 512 tokens (Finardi) foi reescrita sem citação.
   - Taneja: resumos próximos aos do GPT-4o (BERTScore).
   - Touvron (LLaMA-13B em uma GPU) e Carlos (Llama 3.2 via Ollama) no lugar de "3-7 bilhões".
   - Retirada a citação de Thesen e Park da base inspecionável.
   - Johnson saiu da frase sobre abordagens híbridas.
9. Seção 6.2: "reordenação via RRF (KARPUKHIN)" passou a "fusão dos resultados, por exemplo pela técnica Reciprocal Rank Fusion (RRF)", sem citação, porque Karpukhin não usa RRF.
10. Capítulo 7: "ganhos de precisão, relevância e satisfação" passou a "ganhos de aprendizagem e boa aceitação pelos estudantes".
11. Apêndice A.5: retirada a citação de Karpukhin e Johnson da frase sobre o reordenador monoPTT5.

Referências:
- CHERUBINI et al. (Ital-IA 2024, CEUR v. 3762, p. 54-59) e FERREIRA, M. S. (TCC IFSP, com link) refeitas.
- KARPUKHIN passou para os anais do EMNLP 2020, com DOI.
- MAJ et al. passou para a European Research Studies Journal, v. 27, com DOI.
- TASCHETTO, L. de C.; FILETO, R., com Florianópolis e p. 799-805.
- THESEN; PARK passou do artigo de notícia para o artigo da npj Digital Medicine, v. 8, art. 627, com DOI.
- YAHAYA (Jurnal Pendidikan Malaysia, com link).
- FINARDI: incluído COSTA, P., e acentuado CARIDÁ.
- RODRIGUES: p. 1401-1414.
- DOI incluído em LANG, MILADI, PAMPEL, RYU, SONG, TANEJA e WOHLIN (este também com p. 1-10). VETLUZHSKIKH com p. 8:1-8:10.
- LOURES removido.

## Revisão de 5 nov. 2026: correções da conferência com as obras-fonte

Arquivo gerado: Dissertacao_DeepEdu_revisada_5nov.docx (e .pdf), a partir de Dissertacao_DeepEdu_revisada.docx. Paginação e sumário inalterados (98 páginas). Detalhes e evidências em conferencia/RELATORIO_CONFERENCIA.md.

1. RAG Acadêmico (UFRGS): o autor é Leonardo Luis Carlos. "Silva (2025)" passou a "Carlos (2025)" (seção 5.8); "SILVA, 2025" passou a "CARLOS, 2025" na seção 6.1 e na seção A.3. Referência refeita (CARLOS, L. L.; Bacharelado em Engenharia de Computação) e movida para antes de CARNEIRO.
2. "MACHADO; SOUZA; DIAS, 2024" passou a "SOUZA; SOUZA; DIAS, 2024" (seções 5.7 e 5.9). Referência: SOUZA, A. H. N. M. de; SOUZA, I. M. de; DIAS, J. C. [...] Interface Tecnológica, v. 21, n. 2, p. 15-26, 2024; movida para antes de TANEJA.
3. Seção 5.9: "Ayala e Bechard (2024)" passou a "Béchard e Ayala (2024)"; "para menos de 7%" passou a "para menos de 7,5% nos passos e de 4,5% nas tabelas".
4. BNCC de Matemática: páginas corrigidas para a numeração impressa: CE1 537→532; CE2 538→534; CE3 540→535; CE4 543→538; CE5 545→540; EM13MAT315 542→537; EM13MAT102 538→533.
5. Complemento de Computação: páginas corrigidas: competências do EM 65→61 (3 ocorrências); EM13CO10 68→64; EM13CO14 70→66; EM13CO06 66→62; EM13CO07 68→64; EM13CO08 68→64; a síntese da seção 3.2 deixou de indicar a p. 15.
6. Citação direta da EM13CO08: "on line" passou a "on-line", como no original.
7. Referência de Estrela et al.: "NETO, C. de S. S." passou a "SOARES NETO, C. de S."; acrescentado o DOI 10.5753/sbie.2024.242585.
8. LIMA, M. V. de S. (2026) passou a ser citado com iniciais (seções 1.6, 4.3, 5.1, 5.8, 6.1 e 6.2), para distinguir de LIMA, E. R. D. (2026).
9. Referência de Bordin et al.: acrescentadas as páginas 886-892.
10. Lewis et al. (2020) foi retirado de três frases que o artigo não sustenta (atribuição com hiperlinks, seção 4.2; versionamento da base, seção 4.3; taxonomia versionada, seção 6.1). Na seção 2.5, a citação passou a acompanhar apenas a separação entre recuperação e geração.
11. Seção 5.1: a frase sobre "múltiplos índices vetoriais especializados por domínio" passou a descrever o que Lima, M. V. de S. (2026) faz: busca vetorial com filtros de metadados (curso, módulo e tópico).
12. Seção 6.1 (Painel de Governança): Albuquerque et al. (2024) passou a sustentar apenas as métricas de precisão e recall derivadas de feedback implícito.
13. Seção 5.8: Orrenius, Bartczak, Maj et al. e Chiras passaram a ser indicados como citados por Araújo (2025), com "apud" nas frases com resultados numéricos (NBR 10520).
14. Seções 2.4 e 4.2: "usuários infantis registrados" passou a "usuários crianças e adolescentes registrados" (art. 31 da Lei 15.211).
15. Seção 5.9: "a RAG é mais aplicado" passou a "a RAG é mais aplicada".
16. Referências: travessão uniformizado (—) em BARTCZAK, HENRIQUES, OLIVEIRA, ORRENIUS e RIZZI; acrescentadas as páginas de BOSTROM; YUDKOWSKY (p. 316-334) e de BROWN et al. (p. 1877-1901); o negrito de HENRIQUES passou a cobrir só o título.

## Revisão de 2 nov. 2026: referência de Rizzi conferida com o PDF

O autor localizou o PDF de RIZZI (2024): Master's Degree Thesis em Data Science and Engineering, Politecnico di Torino, out. 2024 (orientador: Paolo Garza). A referência passou de "[Conferir: Tese (Doutorado) ou Dissertação (Mestrado)]" para "Dissertação (Mestrado em Data Science and Engineering)". A menção na seção 5.8 (RAG e consultas SQL em chatbot corporativo) confere com o trabalho e não foi alterada.

Na mesma revisão, o autor localizou o PDF de HENRIQUES (2024): Pedro Duarte Santos Henriques, dissertação do Mestrado em Engenharia Informática (Sistemas Inteligentes), Faculdade de Ciências e Tecnologia da Universidade de Coimbra, jul. 2024. A referência passou a indicar o curso e a faculdade. O que a seção 5.8 atribui ao trabalho (seleção de contexto em duas fases) confere com o texto integral ("two-step approach" aplicado a Text-to-SQL; ganho de 2% na acurácia, cerca de 30% mais instâncias processadas).

Ainda nesta revisão, a pedido do autor, foram retirados ROSSI (2024) e SYRJÄ (2024), cujas referências continuavam incompletas (sem tipo de trabalho, instituição e URL). Na seção 5.8, os dois saíram da lista de trabalhos internacionais; a expressão "desde estatísticas esportivas e chatbots corporativos" (Syrjä tratava de estatísticas esportivas) passou a "desde chatbots corporativos e atendimento ao cliente" (Rizzi e Maj et al.). As duas entradas foram removidas das referências.

## Revisão de 1º nov. 2026 (noite, 3): busca dos seis trabalhos não confirmados

A pedido do autor, os seis trabalhos foram procurados em repositórios institucionais e em buscadores acadêmicos. Os não localizados foram retirados; os localizados tiveram a referência completada.

Localizados (referência completada):
1. BARTCZAK (2024) — Degree Project, Uppsala Universitet (DiVA, diva2:1905130).
2. ORRENIUS (2024) — Degree Project, KTH Royal Institute of Technology (DiVA, diva2:1887429).
3. HENRIQUES (2024) — Dissertação de mestrado, Universidade de Coimbra (Estudo Geral, handle 10316/116586).
4. PLUTO (UFAL) — o autor é Enrique Santos de Oliveira (TCC em Ciência da Computação, Campus Arapiraca, 2025). A citação "Santos (2025)" passou a "Oliveira (2025)", a referência foi refeita e movida para a posição alfabética.

Retirados (não localizados):
5. ERIKSSON (2024) — retirado da lista de trabalhos internacionais da seção 5.8 e das referências; com ele saiu a menção a "recuperação de informações em bases de patentes", que se referia a esse trabalho.
6. FERREIRA (2026, UFRR) — foi localizada apenas a banca de qualificação (PROFNIT/UFRR, dez. 2025), sem os resultados citados (RAGAS 0,866/0,864; 80% de acurácia). Foram retirados o parágrafo da seção 5.8, a menção no capítulo 4 ("conforme demonstrado por Borges (2025) em contexto brasileiro") e a entrada das referências.

Observação: os números atribuídos a Orrenius (8,5%) e Bartczak (custo computacional) e a seleção em duas fases de Henriques seguem a revisão de Araújo (2025), citada no mesmo parágrafo; convém conferi-los no texto integral de cada trabalho (links na referência).

Sumário sem alteração (98 páginas).

## Revisão de 1º nov. 2026 (noite, 2): referências conferidas com os PDFs dos artigos

O autor localizou os PDFs de Aquino et al. (2024), Albuquerque et al. (2024), Béchard e Ayala (2024) e Bordin et al. (2025). A conferência resultou nos ajustes abaixo; Bordin et al. (2025) conferiu integralmente e não foi alterado.

1. Capítulo 4 (Prevenção de Riscos e Alucinações): "em contextos educacionais (NOUALI; BADACHE; BELLOT, 2025; AYALA; BECHARD, 2024)" passou a "em contextos educacionais (NOUALI; BADACHE; BELLOT, 2025) e reduzem a alucinação na geração de saídas estruturadas em aplicações corporativas (BÉCHARD; AYALA, 2024)". O artigo trata de geração de fluxos de trabalho em JSON em ambiente corporativo (ServiceNow), não de contexto educacional.
2. Capítulo 4 (Métricas de Avaliação de Qualidade): Albuquerque et al. (2024) saiu da frase sobre o RAGAS, pois o artigo não usa esse framework; foi acrescentada a frase "Como alternativa à avaliação automática, Albuquerque et al. (2024) propuseram a avaliação de aplicações RAG por meio de feedback implícito, derivado das ações dos usuários sobre as respostas geradas."
3. Referências: "AQUINO, J. et al." passou a "AQUINO, I. V. de et al." (primeira autora: Isabella V. de Aquino); acrescentados local (Florianópolis) e páginas (p. 280-287).
4. Referências: em Albuquerque et al. (2024), acrescentados local (Florianópolis) e páginas (p. 253-259).
5. Referências: "AYALA, O.; BECHARD, P." passou a "BÉCHARD, P.; AYALA, O. M.", na ordem de autoria do artigo, e a entrada foi movida para a posição alfabética (depois de BARTCZAK).
6. Sumário sem alteração: os títulos permanecem nas mesmas páginas (98 páginas no total).

## Revisão de 1º nov. 2026 (noite): retirada de dois trabalhos não confirmados

A pedido do autor, foram retirados do texto dois trabalhos de difícil confirmação (um de acesso pago e um artigo de evento não localizado/publicado integralmente). Nenhum dos dois tinha entrada na lista de referências; ambos estavam sem autoria indicada no texto.

1. Seção 5.3 — removido o parágrafo "Um sistema de aprendizado adaptativo baseado em agentes, com arquitetura de três camadas [...] redução de 95% no tempo de criação de conteúdo [...] [inserir fonte]" (trabalho "Scalable Personalized Education Through Agent-orchestrated Retrieval-Augmented Learning").
2. Seção 5.3 — "Taneja et al. (2025) corroboram esses achados, demonstrando que" passou a "Taneja et al. (2025) demonstraram que", porque o parágrafo anterior deixou de existir.
3. Seção 5.3 — título alterado de "Aprendizagem Personalizada em Larga Escala" para "Aprendizagem Personalizada com Agentes" (no texto e no sumário), pois o trabalho que sustentava a ideia de larga escala foi retirado.
4. Seção 5.8 — removido o parágrafo "Em evento nacional, foi apresentado o desenvolvimento de um Tutor Inteligente Interativo para alunos de graduação online em Pedagogia [...] [inserir autoria, evento e ano]" (artigo da Realize Editora sobre o projeto finalista do Prêmio Semesp).
5. Lista de abreviaturas — removida a sigla CSAT (Customer Satisfaction Score), usada só no parágrafo retirado.
6. Sumário, lista de figuras e lista de quadros — números de página ajustados (a partir da seção 5.5, uma página a menos). Ao abrir no Word, convém usar "Atualizar campo" no sumário para confirmar.

## Pendências que dependem do autor

- Campos destacados em amarelo: cidade, ano, ficha catalográfica, banca.
- "Acesso em: [data]" em 9 referências (BRASIL ×3, CEIA-UFG, FERREIRA et al., FONSECA et al., SILVA, SOARES et al., THESEN; PARK).
- Referências incompletas: BARTCZAK, ERIKSSON, ORRENIUS, ROSSI, SYRJÄ, FERREIRA [iniciais], SILVA [prenome], HENRIQUES, RIZZI, SANTOS.
- A.5: rever as citações KARPUKHIN et al. (2020) e JOHNSON; DOUZE; JÉGOU (2019) e incluir a referência do monoPTT5.
- A.6 e 6.4: indicar a fonte do número "0,49 bilhão de parâmetros" (cartão do modelo no Hugging Face).

## Alterações feitas

### 1. Seção 6.4

- Antes: trilha de auditoria e verificação administrativa de vínculo escolar.
- Depois: trilha de auditoria e registro administrativo de matrícula, com referência ao consentimento dos responsáveis.

### 2. Seção 6.4

- Antes: que transforma o telefone do estudante em hash SHA-256 com salt antes do registro em auditoria, e cifragem simétrica do telefone quando é necessário armazená-lo de forma recuperável (phone_vault.py).
- Depois: que transforma o identificador do estudante (o telefone ou, na API local, o identificador informado) em hash SHA-256 com salt antes do registro em auditoria, e cifragem simétrica do telefone quando é necessário armazená-lo de forma recuperável, como na matrícula (phone_vault.py).

### 3. Seção 6.4

- Antes: Segundo, o sistema implementa verificação de consentimento parental a cada mensagem (consent.py e consent_gate.py): nenhuma pergunta é processada sem consentimento ativo e vigente, o aceite é vinculado à referência de consentimento dos responsáveis registrada na matrícula, uma nova versão dos termos exige novo aceite e a revogação remove o histórico da conversa. Os eventos de consentimento usam política fail-closed.
- Depois: Segundo, o sistema implementa verificação de consentimento a cada mensagem (consent.py e consent_gate.py): nenhuma pergunta é processada sem aceite ativo e vigente do estudante; quando há matrícula registrada pela escola, o aceite é associado à referência do consentimento dos responsáveis informada nessa matrícula; uma nova versão dos termos exige novo aceite e a revogação remove o histórico da conversa. Os eventos de consentimento usam política fail-closed. Na versão analisada, a existência de matrícula verificada não é condição para o atendimento.

### 4. Capítulo 7

- Antes: verificação de consentimento parental a cada mensagem, com revogação
- Depois: verificação de consentimento a cada mensagem, com revogação

### 5. Seção A.2

- Antes: o consentimento parental (app/audit/consent.py)
- Depois: o consentimento (app/audit/consent.py)

### 6. Seção A.9

- Antes: implementa a camada de consentimento parental do DeepEdu, relacionada ao art. 12, § 2º, da Lei nº 15.211/2025.
- Depois: implementa a camada de consentimento do DeepEdu, relacionada ao art. 12, § 2º, da Lei nº 15.211/2025. O consentimento dos responsáveis é registrado pela escola na matrícula (endpoint administrativo /admin/students/enroll), e sua referência é associada ao aceite do estudante quando a matrícula existe; na versão analisada, a matrícula não é exigida para o atendimento.

### 7. Seção A.9.1

- Antes: declara a autorização dos responsáveis,
- Depois: declara a autorização dos responsáveis (declaração que, na versão analisada, não é conferida pelo sistema antes de ser exibida),

### 8. Seção A.9.5

- Antes: Desse modo, nenhuma pergunta é respondida sem consentimento ativo e vigente, e cada recusa de processamento fica registrada na trilha de auditoria.
- Depois: Desse modo, nenhuma pergunta é respondida sem aceite ativo e vigente do estudante, e cada recusa de processamento fica registrada na trilha de auditoria. O endpoint /perguntar não exige autenticação: o identificador student_id é informado pelo cliente, o que atende à execução local da prova de conceito, mas exigiria autenticação em implantação real.

### 9. Seção A.14

- Antes: Integração escolar simulada: o vínculo escolar é verificado administrativamente.
- Depois: Integração escolar simulada: a matrícula e o consentimento dos responsáveis são registrados administrativamente, mas não são exigidos no fluxo de atendimento, e a API local não autentica o estudante.

### 10. Seção A.15

- Antes: Auditoria de viés, estudos de escalabilidade e extensão a outras disciplinas.
- Depois: Auditoria de viés, estudos de escalabilidade e extensão a outras disciplinas, além da exigência de matrícula verificada e de autenticação do estudante no fluxo de atendimento.

### 11. Seção A.14

- Antes: Barreira e validação de saída baseadas em listas de padrões: cobrem tentativas e termos conhecidos, podem deixar passar variações não previstas e, eventualmente, bloquear respostas legítimas;
- Depois: Barreira de entrada e validação de saída baseadas em listas fixas de palavras e expressões: por não interpretarem o sentido do texto, podem não detectar formulações ausentes da lista e podem bloquear respostas legítimas que contenham algum dos termos listados;

### 12. Seção A.4

- Antes: corpus.document_added (um por documento)
- Depois: corpus.document_added (um por documento carregado, o que, no caso de PDFs, corresponde a cada página)

### 13. Seção A.5

- Antes: nesse caso, os três primeiros trechos da busca híbrida são mantidos.
- Depois: nesse caso, os três primeiros trechos da busca híbrida são mantidos. O mesmo ocorre, com emissão de aviso, quando o modelo de reordenação não pode ser carregado ou executado.

### 14. Seção A.5.1.4

- Antes: rerank_model: o modelo de reordenação ativo;
- Depois: rerank_model: o modelo de reordenação configurado (registrado mesmo quando, por falha do reordenador, prevalece a ordem da busca híbrida);

### 15. Seção A.12

- Antes: executados automaticamente a cada envio ao repositório por integração contínua
- Depois: executados automaticamente por integração contínua a cada envio ao ramo principal e a cada pull request

### 16. Seção A.12

- Antes: Na execução correspondente à versão analisada, os 59 testes foram executados sem falhas, dos quais 9 foram ignorados pelo próprio ambiente de integração por dependerem de bibliotecas pesadas (como o modelo de linguagem) não instaladas nesse ambiente.
- Depois: Na versão analisada, os 59 testes foram executados sem falhas em ambiente local com todas as dependências instaladas; no ambiente de integração contínua, 9 deles são ignorados por dependerem da biblioteca PyTorch, que não é instalada nesse ambiente.

### 17. Seção A.12

- Antes: e ordem correta das chamadas no pipeline.
- Depois: e, por inspeção do código-fonte, a ordem das chamadas no pipeline.

### 18. Seção A.3

- Antes: O Quadro 2 apresenta as versões fixadas no arquivo requirements.txt.
- Depois: O Quadro 2 apresenta as versões declaradas nos arquivos requirements.txt e control_panel/requirements-control.txt (este último, para o painel administrativo).

### 19. Seção A.4.1

- Antes: e é registrada pelo evento index.restored, em modo fail-closed.
- Depois: e é registrada pelo evento index.restored, em modo fail-closed. Como a substituição da base ocorre antes do registro, uma falha na auditoria interrompe a operação, mas não desfaz a restauração.

### 20. Seção A.7.4

- Antes: em cinco grupos: violência e autolesão, conteúdo sexual, drogas, armas e ofensas.
- Depois: em quatro grupos: violência e autolesão, conteúdo sexual, drogas e armas, e ofensas.

### 21. Seção A.4.1

- Antes: INDEX_VERSIONS_DIR//chroma
- Depois: INDEX_VERSIONS_DIR/<versão>/chroma

### 22. Seção A.11

- Antes: –com-llm
- Depois: --com-llm

### 23. Capítulo 4

- Antes: assegura que a proveniência da informação seja mantida
- Depois: contribui para que a proveniência da informação seja mantida

### 24. Capítulo 4

- Antes: garantindo a privacidade dos dados do aluno
- Depois: favorecendo a privacidade dos dados do aluno

### 25. Capítulo 4

- Antes: é essencial para garantir que respostas geradas
- Depois: permite verificar se respostas geradas

### 26. Capítulo 4

- Antes: são essenciais para mitigar riscos e garantir a justiça
- Depois: contribuem para mitigar riscos e promover a justiça

### 27. Capítulo 5

- Antes: eliminando a dependência de APIs de nuvem
- Depois: reduzindo a dependência de APIs de nuvem

### 28. Capítulo 5

- Antes: infraestrutura fundamental para sistemas educacionais
- Depois: infraestrutura relevante para sistemas educacionais

### 29. Capítulo 6

- Antes: implantado localmente para garantir soberania de dados
- Depois: implantado localmente para favorecer a soberania de dados

### 30. Capítulo 6

- Antes: por eliminar a dependência de APIs proprietárias
- Depois: por reduzir a dependência de APIs proprietárias

### 31. Capítulo 6

- Antes: credenciais que asseguram a verificação de idade
- Depois: credenciais vinculadas à verificação de idade

### 32. Seção 6.4

- Antes: desenvolveu uma implementação funcional denominada DeepEdu
- Depois: desenvolveu uma implementação denominada DeepEdu

### 33. Seção A.3

- Antes: código aberto, para garantir soberania e auditabilidade
- Depois: código aberto, para favorecer a soberania e a auditabilidade

### 34. Capítulo 7

- Antes: foi confirmada no plano da viabilidade técnica
- Depois: encontra sustentação no plano da viabilidade técnica

### 35. Capítulo 7

- Antes: podem coexistir em um sistema funcional,
- Depois: podem ser implementados em conjunto em um mesmo sistema,

### 36. Referências

- Antes: Repositório GitHub. Disponível em: https://github.com/edidiodantas/deepEdu. Acesso em: [data].
- Depois: Repositório GitHub. Disponível em: https://github.com/edidiodantas/deepEdu. Acesso em: 1 nov. 2026.
