# Checklist LGPD + segurança — CloudTask AI SaaS

Lista de verificação para a entrega final. Marque cada item. É um material
**didático e introdutório** — não substitui assessoria jurídica real.

> Base conceitual: [`../conceitos/security-model.md`](../conceitos/security-model.md).

---

## 1. Dados pessoais — mapeamento

- [x] Sei **quais** dados pessoais a aplicação coleta (no CloudTask: praticamente
      nenhum — tarefas são texto livre; cuidado se o usuário digitar dados
      pessoais no título/descrição).
- [x] Sei **onde** cada dado é armazenado (PostgreSQL/RDS, S3, DynamoDB).
- [OK] Sei **por quanto tempo** os dados ficam (retenção) e **como** são apagados.

## 2. Bases legais e finalidade (LGPD art. 6–11)

- [x] A coleta tem **finalidade específica** e informada.
- [OK] Há **base legal** (consentimento, execução de contrato, etc.) — em projeto
      didático, documentar a finalidade já cumpre o exercício.

## 3. Segurança técnica (LGPD art. 46 — medidas de segurança)

- [OK] **Em trânsito:** TLS/HTTPS na borda (ALB + ACM). Sem dado em HTTP aberto.
- [OK] **Em repouso:** criptografia ativa — S3 (`S3_MANAGED`), RDS (encryption),
      DynamoDB (padrão). Confirme nos recursos criados.
- [x] **Segredos** não estão no código nem no git: `.env` e `secret.yaml` no
      `.gitignore`; em produção, Secrets Manager / SSM.
- [x] **Bucket S3 privado** (Block Public Access), acesso só por URL pré-assinada.
- [OK] **Credenciais temporárias** (roles) em vez de chaves fixas no deploy.
- [OK] **Menor privilégio**: a app/role acessa só o que precisa.

## 4. Direitos do titular (LGPD art. 18)

- [x] Existe caminho para **acessar** os dados de um titular (ex.: consultar/
      exportar suas tarefas).
- [OK] Existe caminho para **excluir** (DELETE de tarefas + remoção de uploads).
- [OK] Logs de eventos (DynamoDB) **não** guardam dado sensível desnecessário.

## 5. Operação e incidentes

- [OK] **Backups** definidos (RDS tem snapshot automático; S3 versionado).
- [OK] Sei **como reagir** a um vazamento (revogar credencial, rotacionar segredo).
- [OK] **Cost/uso** monitorado (Budgets) — evita surpresa e uso indevido.

## 6. Higiene de projeto

- [x] Nenhuma **conta AWS real** ou **segredo** commitado (revisar histórico).
- [X] Recursos de teste **destruídos** após cada aula (sem dado órfão na nuvem).
- [x] `README` e docs **não** expõem endpoints/credenciais internos.

---

> ✅ **Entrega:** anexe este checklist preenchido ao
> [`final-report-template.md`](final-report-template.md).