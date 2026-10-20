# Instalação offline (pendrive)

O DeepEdu instala em outro Linux x86_64 **sem internet**, com tudo no pendrive:
código, Python 3.12 portátil, bibliotecas (torch só CPU), modelos de IA,
materiais e índice.

## 1. Gerar o pacote (no PC com internet)

Na pasta do projeto, com o `.venv` já funcionando e o modelo baixado
(`bash scripts/install_hf_model.sh`):

```bash
bash scripts/preparar_pendrive.sh                      # cria ~/DeepEdu-pendrive
bash scripts/preparar_pendrive.sh /media/$USER/PENDRIVE/DeepEdu-pendrive
bash scripts/preparar_pendrive.sh --sem-materiais      # sem PDFs nem índice
```

Copie a pasta gerada inteira para o pendrive. O pacote é dividido em partes de
1,9 GB, então funciona até em pendrive FAT32. Não leva `.env`, chaves nem os
bancos de alunos/auditoria.

## 2. Instalar (no notebook ou servidor, sem internet)

Na pasta do pendrive:

```bash
bash INSTALAR.sh              # notebook: cria o ícone DeepEdu
bash INSTALAR.sh --servidor   # servidor: painel na rede (porta 8501) e liga no boot
```

O instalador confere se o pacote está íntegro, instala em `~/deepEdu`, gera
chaves novas (a de administrador fica em `~/deepEdu/CHAVE_ADMIN.txt`) e grava
`HF_HUB_OFFLINE=1` no `.env` para os modelos não tentarem a internet.

Rodar de novo **atualiza** o programa e mantém `.env`, chaves e dados.

No servidor, o serviço é `deepedu-local` (`systemctl status deepedu-local`).
Para remover: `bash ~/deepEdu/scripts/instalar_servico.sh --remover`.
