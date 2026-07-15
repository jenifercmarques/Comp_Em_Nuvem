# infra/aws — artefatos AWS (didáticos)

Arquivos de referência para o deploy manual da Semana 4. **Nada aqui contém
credenciais reais** — todos os valores sensíveis são *placeholders* que você
substitui na sua própria conta. JSON não aceita comentários, então as
explicações ficam aqui.

## `task-def-fargate-api-db.json`

Task definition do **ECS Fargate** com **2 containers numa única task**
(`api` + `db` Postgres), versão didática do passo a passo em
[`../../docs/praticas/09-deploy-manual-aws.md`](../../docs/praticas/09-deploy-manual-aws.md) §4.
Roda a app inteira sem cluster EKS — mais simples e barato para uma demo.

> ⚠️ **Postgres efêmero:** o container `db` não tem volume. Ao parar a task,
> **os dados somem** (mesma lição do Kind). Em produção real → Amazon RDS.

### Placeholders — substitua antes de registrar

| Placeholder | O que pôr | Onde aparece |
| --- | --- | --- |
| `<ACCOUNT_ID>` | ID da **sua** conta AWS (`aws sts get-caller-identity --query Account --output text`) | URI da imagem ECR |
| `EXEC_ROLE_ARN` | ARN do `ecsTaskExecutionRole` (deixa o Fargate puxar do ECR + logs) | `executionRoleArn` |
| `TASK_ROLE_ARN` | ARN da role da aplicação (S3/DynamoDB etc.); pode ser igual à exec em demo | `taskRoleArn` |
| `<TROQUE_SENHA_DB>` | senha do Postgres (use uma forte) | `POSTGRES_PASSWORD` e `DATABASE_URL` |
| `<TROQUE_SECRET_KEY>` | `SECRET_KEY` da app (`python -c "import secrets;print(secrets.token_urlsafe(32))"`) | env `SECRET_KEY` |

> 🔐 **Nunca commite segredos reais.** Aqui são placeholders só para a task
> *renderizar*. Numa demo descartável você pode colar valores direto na hora de
> registrar (arquivo local, fora do git). Em produção real, **não** ponha
> segredo em texto plano na task def — use **AWS Secrets Manager** ou **SSM
> Parameter Store** e referencie via `secrets` na container definition.

### Registrar (depois de substituir os placeholders)

```bash
aws ecs register-task-definition --cli-input-json file://infra/aws/task-def-fargate-api-db.json
```
