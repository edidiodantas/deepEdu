# Alterações na dissertação — revisão de 1º nov. 2026

Arquivo de origem: Dissertacao_final (1).docx. Arquivo revisado: Dissertacao_DeepEdu_revisada.docx (e o PDF correspondente).
Os 39 trechos de código do Apêndice A não foram alterados e continuam idênticos ao repositório (commit 6d67901 / main 447364e).

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
