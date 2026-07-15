# AWS CDK (Aula 11)

Estrutura didatica de IaC com CDK em Python.

## Estrutura
- app.py: ponto de entrada CDK.
- stacks/storage_stack.py: bucket S3 para uploads.
- stacks/ecr_stack.py: repositorio ECR cloudtask-api.
- stacks/network_stack.py: VPC basica opcional.

## Setup

```bash
cd infra/cdk
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Comandos principais

```bash
cdk bootstrap aws://<account>/<region>
cdk synth
cdk diff
cdk deploy
```

Para incluir stack de rede opcional:

```bash
ENABLE_NETWORK_STACK=true cdk deploy
```

Para destruir:

```bash
cdk destroy --all
```

## Observacao de custo
- VPC com NAT gera custo por hora.
- Sempre destruir os recursos apos a aula.
