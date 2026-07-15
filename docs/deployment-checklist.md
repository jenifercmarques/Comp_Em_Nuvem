# Checklist de deploy + custos — CloudTask AI SaaS

Rode esta lista **antes** de demonstrar/entregar e **depois** para garantir que
nada ficou cobrando. Vale para o deploy final (EKS/RDS/ALB) ou para qualquer
demo na nuvem.

> Comandos de diagnóstico detalhados:
> [`../praticas/99-troubleshooting.md`](../praticas/99-troubleshooting.md) §💸 Custos.

---

## Antes do deploy

- [ ] Credenciais AWS válidas: `aws sts get-caller-identity` retorna seu ARN.
- [ ] Região correta: `aws configure get region` (`us-east-1`).
- [ ] Imagem no ECR: `aws ecr list-images --repository-name cloudtask-api`.
- [ ] `.env` / Secret revisados (sem placeholders tipo `USER:SENHA@HOST`).
- [ ] Banco definido: RDS criado **ou** Postgres como Pod (ciente do trade-off).

## Durante (subir)

- [ ] Cluster EKS pronto: `kubectl get nodes` em `Ready`.
- [ ] metrics-server ok (se for usar HPA): `kubectl top nodes` lista CPU.
- [ ] `kubectl apply -k infra/k8s/aws/` aplicado sem erro.
- [ ] Pods `Running`: `kubectl get pods -n cloudtask`.
- [ ] Serviço acessível: `curl http://<ELB>/health` → 200, `/health/ready` → db ok.

## Verificação funcional (demonstrar)

- [ ] CRUD: criar/listar/atualizar/excluir tarefa (Swagger ou curl).
- [ ] Upload: `POST /uploads` (local ou S3) e download.
- [ ] Evento: criar tarefa gera `task.created` (`GET /events`).
- [ ] (Opcional) HPA: gerar carga e ver réplicas subir/descer.

## 🔥 Depois (destruir — OBRIGATÓRIO)

> Ordem importa: **Service LoadBalancer primeiro** (libera o ELB), cluster por último.

- [ ] `kubectl delete -k infra/k8s/aws/` (apaga workloads + ELB).
- [ ] `eksctl delete cluster --name <cluster>` (ou Console → Delete).
- [ ] RDS apagado (se criado): `aws rds delete-db-instance ... --skip-final-snapshot`.
- [ ] DynamoDB apagado: `aws dynamodb delete-table --table-name cloudtask-events`.
- [ ] S3 de teste apagado.
- [ ] `cdk destroy --all` (se usou CDK).

## Sweep final (tudo vazio = zero cobrança)

```bash
aws eks list-clusters --region us-east-1 --query clusters --output text
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running,pending" --query "Reservations[].Instances[].InstanceId" --output text --region us-east-1
aws elbv2 describe-load-balancers --query "LoadBalancers[].DNSName" --output text --region us-east-1
aws ec2 describe-nat-gateways --filter "Name=state,Values=available,pending" --query "NatGateways[].NatGatewayId" --output text --region us-east-1
aws ec2 describe-addresses --query "Addresses[?AssociationId==null].PublicIp" --output text --region us-east-1
aws rds describe-db-instances --query "DBInstances[].DBInstanceIdentifier" --output text --region us-east-1
```

- [ ] Tudo acima **vazio**.
- [ ] (24h depois) Cost Explorer / Billing sem gasto inesperado.