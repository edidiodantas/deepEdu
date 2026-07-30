# Segurança de Dados em Repouso — deepEdu

| Campo | Valor |
|-------|-------|
| **Versão** | 1.0 |
| **Requisitos** | RF30, RNF13, RNF16 |
| **Data** | 29/06/2026 |

---

## 1. Camadas de proteção

| Camada | Implementação | Status |
|--------|---------------|--------|
| **Aplicação** | Telefone criptografado (Fernet) em `phone_vault` | Implementado |
| **Identificadores** | `phone_hash` + `session_id` pseudonimizado | Implementado |
| **Banco SQLite** | Permissões restritas (`chmod 600`) no volume | Deploy |
| **Volume** | LUKS/dm-crypt no servidor Ubuntu | Infraestrutura |
| **Backup** | `scripts/backup_data.sh` com retenção configurável | Implementado |

---

## 2. Configuração recomendada (produção)

```bash
# Permissões dos bancos
chmod 600 data/audit/audit.db data/chat_history/chat_history.db data/billing/billing.db

# Backup diário (cron)
0 2 * * * /home/USUARIO/Projects/deepEdu/scripts/backup_data.sh >> /var/log/deepedu_backup.log 2>&1

# Criptografia de volume (LUKS) — executar na instalação do servidor
# Ver: https://help.ubuntu.com/community/Full_Disk_Encryption_Howto_2019
```

---

## 3. Validação em startup

`app/core/startup_checks.py` bloqueia subida em `ENV=production` se:
- `AUDIT_PHONE_SALT` < 16 caracteres
- `PHONE_ENCRYPTION_KEY` ausente ou placeholder
- `ADMIN_API_KEY` fraca
- `AUDIT_FAIL_CLOSED` desligado

---

## 4. Checklist operacional

- [ ] Volume `/data` em LUKS ou disco criptografado na nuvem
- [ ] Backups testados (restauração mensal)
- [ ] Chaves Fernet rotacionadas anualmente
- [ ] Acesso SSH apenas por chave
- [ ] Firewall: portas 80/443 públicas; 8000 apenas localhost
