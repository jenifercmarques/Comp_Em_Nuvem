#!/usr/bin/env bash
# =============================================================================
# build-push-ecr.sh — Semana 4 · Aula 7 — build da imagem PROD + push para o Amazon ECR.
# -----------------------------------------------------------------------------
# CONTEXTO (Aula 7 — Semana 4):
#   O EKS (cluster na nuvem) NÃO enxerga as imagens da sua máquina. Ele puxa
#   de um "registry" — o GitHub das imagens Docker. Na AWS esse registry é o
#   ECR (Elastic Container Registry), privado e integrado ao IAM.
#
#   Fluxo desta etapa:  build  ->  tag  ->  login  ->  push
#   (depois, na Aula 8, o EKS faz o `pull` a partir do ECR.)
#
# POR QUÊ `--target prod`:
#   O Dockerfile é multi-stage. A imagem que vai para a nuvem deve ser a
#   ENXUTA (sem pytest, sem ferramentas de debug). `prod` é esse estágio.
#
# PRÉ-REQUISITOS:
#   * AWS CLI v2 configurada (Learner Lab: copie as credenciais temporárias).
#   * Docker disponível (no devcontainer funciona via docker-outside-of-docker).
#   * Permissão IAM para ECR (no Learner Lab a LabRole já cobre).
#
# COMO USAR:
#   ./scripts/semana-04-ecr/build-push-ecr.sh                 # usa os defaults abaixo
#   REGION=us-east-1 REPO=cloudtask-api TAG=latest ./scripts/semana-04-ecr/build-push-ecr.sh
#   TAG="$(git rev-parse --short HEAD)" ./scripts/semana-04-ecr/build-push-ecr.sh   # tag = SHA
#
# CUSTO: ECR cobra centavos por GB-mês de armazenamento. Bem barato. O caro
#   da semana é o EKS (Aula 8), não o ECR.
# =============================================================================

# `set -euo pipefail`: aborta no primeiro erro (-e), trata variável não
# definida como erro (-u) e propaga falha em pipes (-o pipefail). Evita
# "seguir em frente" com um passo quebrado — importante em script de deploy.
set -euo pipefail

# ---------------------------------------------------------------------------
# Parâmetros (sobrescreva por variável de ambiente, ver exemplos no cabeçalho).
# ---------------------------------------------------------------------------
REGION="${REGION:-us-east-1}"
REPO="${REPO:-cloudtask-api}"
TAG="${TAG:-latest}"
DOCKERFILE_TARGET="${DOCKERFILE_TARGET:-prod}"

# Descobre o ID da conta AWS logada (12 dígitos). Compõe o host do ECR.
ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE_LOCAL="${REPO}:${TAG}"
IMAGE_REMOTE="${REGISTRY}/${REPO}:${TAG}"

echo "==> Conta AWS : ${ACCOUNT}"
echo "==> Região    : ${REGION}"
echo "==> Repositório: ${REPO}   Tag: ${TAG}"
echo "==> Imagem ECR : ${IMAGE_REMOTE}"
echo

# ---------------------------------------------------------------------------
# 1. Garante que o repositório existe (idempotente).
#    `describe-repositories` falha se não existir; nesse caso, criamos.
# ---------------------------------------------------------------------------
if ! aws ecr describe-repositories --repository-names "${REPO}" --region "${REGION}" >/dev/null 2>&1; then
  echo "==> Repositório '${REPO}' não existe. Criando..."
  aws ecr create-repository \
    --repository-name "${REPO}" \
    --image-scanning-configuration scanOnPush=true \
    --region "${REGION}" >/dev/null
  echo "    criado."
else
  echo "==> Repositório '${REPO}' já existe. Reutilizando."
fi

# ---------------------------------------------------------------------------
# 2. Login do Docker no ECR.
#    O token dura ~12h. Se der `denied` no push mais tarde, refaça este login.
# ---------------------------------------------------------------------------
echo "==> Fazendo login do Docker no ECR..."
aws ecr get-login-password --region "${REGION}" \
  | docker login --username AWS --password-stdin "${REGISTRY}"

# ---------------------------------------------------------------------------
# 3. Build da imagem PROD e tag apontando para o ECR.
# ---------------------------------------------------------------------------
echo "==> Build (--target ${DOCKERFILE_TARGET})..."
docker build --target "${DOCKERFILE_TARGET}" -t "${IMAGE_LOCAL}" .

echo "==> Tag ${IMAGE_LOCAL} -> ${IMAGE_REMOTE}"
docker tag "${IMAGE_LOCAL}" "${IMAGE_REMOTE}"

# ---------------------------------------------------------------------------
# 4. Push para o ECR.
# ---------------------------------------------------------------------------
echo "==> Push para o ECR..."
docker push "${IMAGE_REMOTE}"

echo
echo "==> Pronto. Imagens no repositório:"
aws ecr list-images --repository-name "${REPO}" --region "${REGION}" --output table

echo
echo "Use esta imagem no Deployment do EKS (infra/k8s/aws/deployment-eks.yaml):"
echo "    image: ${IMAGE_REMOTE}"