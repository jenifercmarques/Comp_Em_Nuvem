# Deploy no EKS (Aula 8)

Este diretoria contem os manifests base para deploy da API no EKS e os dois
caminhos de HTTPS pedidos na aula.

Arquivos principais:
- deployment-eks.yaml: deployment com 2 replicas, requests/limits, liveness/readiness.
- service-loadbalancer.yaml: Service LoadBalancer para expor a API.
- configmap.yaml: configuracoes nao sensiveis (FORCE_HTTPS e BEHIND_PROXY coerentes com proxy).
- secret.example.yaml: template de secret (copiar para secret.yaml local).
- ingress-alb-acm.example.yaml: caminho ideal com ALB + ACM + redirect 80->443.

## Pre-requisitos

- Imagem cloudtask-api publicada no ECR.
- AWS CLI v2 + kubectl + eksctl instalados.
- Cluster EKS acessivel:
	aws eks update-kubeconfig --name <cluster> --region <region>

## Passo a passo (base)

1) Atualizar kubeconfig:
aws eks update-kubeconfig --name <cluster> --region us-east-1

2) Criar secret real fora do versionamento:
cp infra/k8s/aws/secret.example.yaml infra/k8s/aws/secret.yaml
Edite valores reais e descomente secret.yaml em kustomization.yaml.

3) Aplicar manifests base:
kubectl apply -k infra/k8s/aws/
kubectl get pods -n cloudtask
kubectl get svc -n cloudtask

4) Testar health endpoints via Service/ELB:
LB=$(kubectl get svc cloudtask-api -n cloudtask -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl http://$LB/health
curl http://$LB/health/ready

## HTTPS na borda: dois caminhos

### Caminho ideal (conta com dominio proprio)

Aplicar ingress-alb-acm.example.yaml (ajuste host e certificate-arn):
kubectl apply -f infra/k8s/aws/ingress-alb-acm.example.yaml

Validacoes esperadas:
- https://<host> responde normalmente.
- http://<host> redireciona para https:// (ssl-redirect no ALB).

### Caminho Learner Lab (sem dominio)

Limitacao: ACM exige validacao DNS, normalmente indisponivel no lab.
Nesse caso, mantenha HTTP no ELB via Service LoadBalancer (manifest base).
Comentario de arquitetura: aqui entraria ACM em producao real.
O entendimento de HTTPS fica coberto pela pratica local com mkcert (Aula 4).

## Decisoes e riscos (resumo)

- ssl-redirect no ALB, nao no app:
	por que: redirect num lugar so.
	impacto: app fica simples.
	risco: loop de redirect e pod unhealthy se fizer no app atras de proxy.

- readiness em /health/ready:
	por que: recebe trafego so com DB disponivel.
	impacto: rollout espera dependencia.
	risco: readiness em /health aceita trafego com DB fora.

- liveness em /health:
	por que: reinicia apenas travamento do processo.
	impacto: auto-healing correto.
	risco: liveness no DB reinicia pod por falha externa.

- certificado no ACM:
	por que: gratis e auto-renovado.
	impacto: sem operacao manual de certificado.
	risco: certificado manual expira.

- cluster pequeno (2 nos t3.small/t3.medium):
	por que: teto de credito no Learner Lab.
	impacto: custo baixo para aula.
	risco: nos grandes queimam credito rapidamente.

## Como destruir ao final

kubectl delete -f infra/k8s/aws/
eksctl delete cluster --name <cluster> --region us-east-1

Atencao: EKS + ELB + EC2 cobram por hora ligados.
