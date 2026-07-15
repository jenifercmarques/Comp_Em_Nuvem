# Tarefas das aulas — CloudTask AI SaaS

> **Documento fixo.** Esta é a versão de referência das 12 tarefas da disciplina **Computação em Nuvem** (N-CPU / UNINTER). Serve para qualquer turma e para consulta offline.
>
> A versão "viva" (com status, comentários, marcação de concluída) fica nas [Issues do GitHub](https://github.com/N-CPUninter/Computa-o-em-Nuvem---Projeto-exemplo-CloudTask-AI-SaaS/issues). **Este arquivo não deve ser alterado** conforme as aulas avançam.

---

## Sumário

| Aula | Tema | Branch | Issue |
| ---: | :--- | :----- | :--- |
|  1 | FastAPI mínimo                                    | `semana-01-fastapi-docker`     | #1  |
|  2 | Docker e Docker Compose                           | `semana-01-fastapi-docker`     | #2  |
|  3 | PostgreSQL + CRUD                                 | `semana-02-rds-vpc-seguranca`  | #3  |
|  4 | Config, segurança, HTTPS e health/ready (Postgres) | `semana-02-rds-vpc-seguranca`  | #4  |
|  5 | Upload S3 (com fallback local)                    | `semana-03-s3-kubernetes`      | #5  |
|  6 | Kubernetes local (Kind / Minikube)                | `semana-03-s3-kubernetes`      | #6  |
|  7 | Publicar imagem no Amazon ECR                     | `semana-04-eks-aws`            | #7  |
|  8 | Deploy no Amazon EKS                              | `semana-04-eks-aws`            | #8  |
|  9 | Escalabilidade (HPA), carga e custos              | `semana-05-custos-nosql-logs`  | #9  |
| 10 | Eventos/logs com DynamoDB (fallback JSON)         | `semana-05-custos-nosql-logs`  | #10 |
| 11 | Infraestrutura como código com AWS CDK            | `semana-06-cdk-final`          | #11 |
| 12 | Documentação final, LGPD e entrega                | `semana-06-cdk-final`          | #12 |

### Convenções

- Cada **semana** tem uma branch própria que **acumula** o código produzido nas duas aulas daquela semana.
- A branch de uma **nova semana** parte do estado final da semana anterior.
- **Nenhuma** branch é mergeada na `main`. A `main` só recebe atualizações pontuais decididas pelo professor.
- A interface principal de testes é o **Swagger automático da FastAPI** (`/docs`).

---

# Semana 1 — FastAPI + Docker

## Aula 1 — Iniciar a API com FastAPI mínimo

**Branch:** `semana-01-fastapi-docker` · **Issue:** #1
**Labels:** `semana-1`, `aula-01`, `fastapi`, `python`

### Objetivo didático
Apresentar o que é uma API REST, montar a estrutura inicial do projeto **CloudTask AI SaaS** e deixar o esqueleto pronto para receber Docker na próxima aula.

### Pré-requisitos
- Python 3.11+
- pip 23+
- Git

### Entregas (checklist)
- [ ] Criar e ativar ambiente virtual (`python -m venv .venv` e ativar).
- [ ] Criar `requirements.txt` com no mínimo: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`.
- [ ] Criar estrutura inicial de pastas:
  ```text
  app/
    __init__.py
    main.py
    api/
      __init__.py
      routes_health.py
  ```
- [ ] Implementar em `app/main.py` a instância do FastAPI (`title="CloudTask AI SaaS"`).
- [ ] Implementar os endpoints:
  - `GET /` — retorna `{"name": "CloudTask AI SaaS", "version": "0.1.0"}`.
  - `GET /health` — retorna `{"status": "ok"}` com HTTP 200.
- [ ] Atualizar o `README.md` da branch com instruções de execução local.
- [ ] Garantir que `.env.example` está presente (já vem do `main`).
- [ ] Confirmar que `.gitignore` ignora `.venv/`, `__pycache__/`, `.env`.

### Endpoints esperados
```
GET /
GET /health
GET /docs        (Swagger automático da FastAPI)
```

### Critérios de aceite
- `uvicorn app.main:app --reload` sobe sem erro.
- `http://localhost:8000/health` responde `{"status": "ok"}`.
- `http://localhost:8000/docs` abre a interface Swagger.
- Código simples, comentado e organizado em pastas.

### Referências
- [HOW_TO_USE.md](HOW_TO_USE.md)
- [ROADMAP.md — Aula 1](ROADMAP.md)
- FastAPI: <https://fastapi.tiangolo.com/>

---

## Aula 2 — Containerizar a aplicação com Docker e Docker Compose

**Branch:** `semana-01-fastapi-docker` · **Issue:** #2
**Labels:** `semana-1`, `aula-02`, `docker`, `fastapi`

### Objetivo didático
Explicar containers, padronizar a execução da aplicação e preparar o terreno para Kubernetes e cloud-native nas próximas semanas.

### Pré-requisitos
- Docker Desktop 4.30+
- Docker Compose v2 (`docker compose version`)
- Código da Aula 1 funcionando

### Entregas (checklist)
- [ ] Criar `Dockerfile` na raiz do projeto:
  - Imagem base **slim** do Python 3.11.
  - Copiar `requirements.txt` e instalar dependências primeiro (para cache).
  - Copiar o código da aplicação.
  - Expor a porta `8000`.
  - Comando de inicialização com `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- [ ] Criar `docker-compose.yml` com o serviço `api`:
  - `build: .`
  - Mapeamento de porta `8000:8000`.
  - Volume montando o código (para hot-reload em desenvolvimento, opcional).
  - `env_file: .env` (mesmo que ainda vazio).
- [ ] Criar `.dockerignore` (no mínimo: `.git`, `.venv`, `__pycache__`, `.env`, `local_uploads/`).
- [ ] Atualizar `README.md` com a seção **"Rodando com Docker"**:
  ```bash
  docker compose up --build
  docker compose down
  ```
- [ ] Verificar que `GET /health` continua funcionando dentro do container.

### Critérios de aceite
- `docker compose up --build` sobe a API sem erros.
- `http://localhost:8000/health` responde corretamente a partir do container.
- Imagem Docker final < 250 MB (use imagem `slim`).
- Comandos documentados no README.

### Referências
- Dockerfile reference: <https://docs.docker.com/engine/reference/builder/>
- Compose specification: <https://docs.docker.com/compose/compose-file/>
- [ROADMAP.md — Aula 2](ROADMAP.md)

---

# Semana 2 — PostgreSQL/RDS, VPC e Segurança

## Aula 3 — Persistência com PostgreSQL e CRUD de tarefas

**Branch:** `semana-02-rds-vpc-seguranca` · **Issue:** #3
**Labels:** `semana-2`, `aula-03`, `postgresql`, `fastapi`

### Objetivo didático
Apresentar persistência de dados com um banco SQL relacional, mostrar SQLAlchemy + Pydantic e preparar o aluno para comparar com o Amazon RDS na sequência da disciplina.

### Pré-requisitos
- Código funcionando da Semana 1 (FastAPI + Docker)
- Docker Compose v2

### Entregas (checklist)
- [ ] Adicionar serviço **`db`** no `docker-compose.yml` usando imagem oficial `postgres:16`:
  - Usuário, senha e nome de banco vindos de variáveis de ambiente.
  - Volume persistente para os dados (`pgdata:/var/lib/postgresql/data`).
  - `depends_on` configurado no serviço `api`.
- [ ] Adicionar ao `requirements.txt`: `sqlalchemy`, `psycopg2-binary`.
- [ ] Criar `app/db/database.py` com `engine`, `SessionLocal` e `Base` do SQLAlchemy.
- [ ] Criar `app/db/models.py` com o modelo `Task`:
  ```text
  Task:
    - id           (int, PK, autoincrement)
    - title        (str, obrigatório)
    - description  (str, opcional)
    - status       (enum: pending | in_progress | done)
    - priority     (enum: low | medium | high)
    - created_at   (datetime, default now)
    - updated_at   (datetime, auto-update)
  ```
- [ ] Criar `app/db/schemas.py` com schemas Pydantic: `TaskCreate`, `TaskUpdate`, `TaskRead`.
- [ ] Criar `app/api/routes_tasks.py` com os endpoints do CRUD.
- [ ] Registrar o router em `app/main.py`.
- [ ] Garantir criação automática das tabelas no startup (`Base.metadata.create_all`).
- [ ] Atualizar `README.md` da branch com comandos de exemplo `curl` ou Swagger.

### Endpoints esperados
```
POST   /tasks
GET    /tasks
GET    /tasks/{task_id}
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

### Variáveis de ambiente
```
DATABASE_URL=postgresql+psycopg2://cloudtask:cloudtask@db:5432/cloudtask
POSTGRES_USER=cloudtask
POSTGRES_PASSWORD=cloudtask
POSTGRES_DB=cloudtask
```

### Critérios de aceite
- `docker compose up --build` sobe `api` + `db` sem erro.
- É possível criar, listar, ler, atualizar e remover tarefas via Swagger.
- Os dados persistem após `docker compose down` (graças ao volume).
- Validações de entrada via Pydantic funcionam (ex.: `title` vazio é rejeitado).

### Referências
- [ROADMAP.md — Aula 3](ROADMAP.md)
- SQLAlchemy: <https://docs.sqlalchemy.org/>
- Pydantic v2: <https://docs.pydantic.dev/latest/>

---

## Aula 4 — Config por ambiente, segurança, HTTPS e health/ready (PostgreSQL)

**Branch:** `semana-02-rds-vpc-seguranca` · **Issue:** #4
**Labels:** `semana-2`, `aula-04`, `security`, `vpc`, `env-config`, `documentation`

### Objetivo didático
Separar configuração do código, nunca versionar credenciais, **expor a API com HTTPS de forma simples e segura** e introduzir rede/segurança da AWS. Todo código e config desta aula vem **comentado explicando motivo, impacto e risco** de cada decisão (público iniciante).

### Pré-requisitos
- CRUD da Aula 3 funcionando

### Entregas (checklist)

**1. Configuração no código**
- [ ] `app/core/config.py` com `pydantic-settings` (`BaseSettings`).
- [ ] Mover variáveis sensíveis/ambientais para `.env`:
  - `APP_ENV` (development | staging | production)
  - `APP_PORT`, `SECRET_KEY` (gerar com `secrets.token_urlsafe(32)`), `DATABASE_URL`, `LOG_LEVEL`
  - `FORCE_HTTPS` (bool — **única chave** que liga o comportamento de produção)
  - `TRUSTED_HOSTS` (lista de hosts aceitos)
- [ ] `app/main.py` e módulos consomem `settings`.
- [ ] `.env` no `.gitignore`; `.env.example` cobre as novas variáveis (comentado).

**2. Readiness check com PostgreSQL**
- [ ] `GET /health/ready` em `routes_health.py`: executa `SELECT 1` no banco.
  - `200 {"status":"ready","db":"ok"}` quando o banco responde.
  - `503 {"status":"not_ready","db":"down"}` quando falha (capturar exceção).
- [ ] `GET /health` continua **liveness puro** (NÃO toca no banco).
- [ ] Schema Pydantic `ReadyResponse` com exemplos no Swagger.
- [ ] `description=` Markdown explicando **por que** liveness e readiness são separados.

**3. HTTPS / TLS — modelo simples e seguro**
- [ ] Container sobe uvicorn com **`--proxy-headers`** por padrão (e documentar `--forwarded-allow-ips`).
- [ ] App **NÃO** usa `HTTPSRedirectMiddleware` quando atrás de ALB (o redirect é da borda — ver riscos). Middleware só no caso raro de app exposta direto sem proxy.
- [ ] Header **HSTS** somente quando `APP_ENV != development`, `max-age` modesto, **sem `preload`**.
- [ ] `TrustedHostMiddleware` lendo `TRUSTED_HOSTS`.
- [ ] HTTPS local **opcional** com **`mkcert`** (não `openssl` cru): CA local → sem aviso no browser.
- [ ] `docs/conceitos/https-tls.md` didático.

**4. Documentação conceitual (criar em `docs/`)**
- [ ] `docs/conceitos/aws-networking.md`: VPC, subnet pública/privada, SG, IG, NAT, bastion + diagrama (Mermaid/ASCII).
- [ ] `docs/conceitos/security-model.md`: IAM, MFA, responsabilidade compartilhada, criptografia em repouso e **em trânsito** (liga com `https-tls.md`), boas práticas de credenciais, intro LGPD.

> ⚠️ **Nada é provisionado na AWS nesta aula.** HTTPS em prod é exercitado de fato na Aula 8 (ALB + ACM no EKS). Aqui: configurar o app + documentar.

### Decisões e riscos (devem aparecer comentados no código/config)

| Decisão | Por quê | Impacto | Risco se ignorar |
| --- | --- | --- | --- |
| TLS termina **na borda** (ALB), não no app | "App fala HTTP, a porta fala HTTPS" | Cert vive no ALB, não na imagem | Cert na imagem complica e não renova |
| Redirect HTTP→HTTPS **só no ALB** (Aula 8) | Um lugar declarativo | App fica simples | App redireciona + probe HTTP interno = **loop → pod "unhealthy"** |
| App só `--proxy-headers` + HSTS | Confia no `X-Forwarded-Proto` | URLs/redirects corretos | Sem `--proxy-headers`, FastAPI gera **loop** |
| Dev local = **HTTP puro** (`FORCE_HTTPS=false`) | Evita fricção de cert local | Aluno foca no código | Forçar HTTPS local = avisos de browser |
| HTTPS local via **mkcert** | CA local → sem aviso | Aluno *vê* HTTPS | openssl self-signed assusta iniciante |
| Cert prod = **AWS ACM** | Grátis e **auto-renova** | Zero gestão de renovação | Cert manual expira e derruba o site |
| HSTS **sem preload**, só prod | preload é **irreversível** | Browser força HTTPS | preload errado trava o domínio por meses |

### Dois caminhos (por causa do Learner Lab)
- **Ideal (conta/domínio próprios):** ACM + domínio + ALB Ingress + `ssl-redirect` → HTTPS real ponta a ponta.
- **Learner Lab (sem domínio):** ACM precisa de DNS → provável não dar. Demonstrar HTTPS **localmente com mkcert** (todos veem funcionando) e, no EKS, expor HTTP no ELB documentando "aqui entraria o ACM em produção real".

### Critérios de aceite
- `GET /health` responde sem tocar no banco; `GET /health/ready` reflete o estado real do PostgreSQL (200 up / 503 down).
- Atrás de proxy com `FORCE_HTTPS=true`, **sem loop** de redirect (probes OK).
- `git grep -i "password\|secret" app/` não retorna valores reais hardcoded.
- `docs/conceitos/aws-networking.md`, `docs/conceitos/security-model.md`, `docs/conceitos/https-tls.md` existem, completos e **comentados de forma didática**.

### Referências
- [ROADMAP.md — Aula 4](ROADMAP.md)
- pydantic-settings: <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
- Starlette middlewares: <https://www.starlette.io/middleware/>
- mkcert: <https://github.com/FiloSottile/mkcert>
- AWS ACM: <https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html>

---

# Semana 3 — S3, EFS, Data Lake e Kubernetes local

## Aula 5 — Upload de arquivos com Amazon S3 (e fallback local)

**Branch:** `semana-03-s3-kubernetes` · **Issue:** #5
**Labels:** `semana-3`, `aula-05`, `s3`, `aws`, `fastapi`

### Objetivo didático
Mostrar que arquivos **não devem ser armazenados dentro do container**. Apresentar S3 como object storage gerenciado e base para Data Lakes. Garantir que alunos sem AWS consigam executar via fallback local.

### Pré-requisitos
- Aplicação com CRUD funcionando (Semana 2)
- *(Opcional)* Conta no AWS Academy / Learner Lab para testar com S3 real

### Entregas (checklist)
- [ ] Adicionar ao `requirements.txt`: `boto3`, `python-multipart`.
- [ ] Criar `app/services/s3_service.py` com **duas implementações** selecionáveis por variável:
  - **Modo local:** salva os arquivos em `LOCAL_UPLOADS_DIR` (default `./local_uploads`).
  - **Modo S3:** faz `put_object` no bucket configurado.
- [ ] Criar `app/api/routes_uploads.py` com:
  - `POST /uploads` — recebe `UploadFile`, devolve nome/URL.
  - `GET /uploads/{filename}` — baixa o arquivo. Param `?via=redirect|url|stream`:
    `redirect` (default, 307 → URL pré-assinada no S3), `url` (JSON com a URL),
    `stream` (API faz proxy dos bytes; funciona no Swagger, anti-padrão em prod).
- [ ] Registrar o router em `app/main.py`.
- [ ] Adicionar `local_uploads/` ao `.gitignore` (já está, confirme).
- [ ] Criar `docs/conceitos/s3-efs-datalake.md` explicando, de forma didática:
  - Diferença entre **block storage**, **file storage (EFS)** e **object storage (S3)**.
  - Classes de armazenamento do S3 (Standard, IA, Glacier).
  - O que é um **Data Lake** e como o S3 se encaixa.
- [ ] Atualizar `README.md` da branch com instruções para os dois modos.

### Variáveis de ambiente
```
STORAGE_MODE=local            # local | s3
LOCAL_UPLOADS_DIR=./local_uploads
AWS_REGION=us-east-1
S3_BUCKET_NAME=cloudtask-ai-saas-uploads
```

### Critérios de aceite
- Com `STORAGE_MODE=local`: upload e download funcionam usando o disco local.
- Com `STORAGE_MODE=s3` e credenciais válidas: arquivo aparece no bucket.
- Trocar de modo **não** exige alterar código, apenas o `.env`.
- `docs/conceitos/s3-efs-datalake.md` existe e está completo.

### Referências
- [ROADMAP.md — Aula 5](ROADMAP.md)
- boto3 S3: <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html>
- FastAPI UploadFile: <https://fastapi.tiangolo.com/tutorial/request-files/>

---

## Aula 6 — Kubernetes local com Kind ou Minikube

**Branch:** `semana-03-s3-kubernetes` · **Issue:** #6
**Labels:** `semana-3`, `aula-06`, `kubernetes`, `docker`

### Objetivo didático
Apresentar Kubernetes: pods, deployments, services, replicas e auto-healing. Rodar a aplicação localmente em cluster Kind/Minikube como preparação para o EKS na Semana 4.

### Pré-requisitos
- Imagem Docker da aplicação rodando (Aula 2)
- Instalar **Kind** *ou* **Minikube**
- Instalar **kubectl** (`kubectl version --client`)

### Entregas (checklist)
- [ ] Criar pasta `infra/k8s/` com os manifests:
  - [ ] `namespace.yaml` — namespace `cloudtask`.
  - [ ] `deployment.yaml` — Deployment com **no mínimo 2 réplicas** da API.
  - [ ] `service.yaml` — Service do tipo `ClusterIP` ou `NodePort`.
  - [ ] `configmap.yaml` — variáveis não-sensíveis.
  - [ ] `secret.example.yaml` — modelo de Secret (sem valores reais; o real fica fora do repo).
- [ ] Construir a imagem localmente e carregá-la no cluster:
  - Kind: `kind load docker-image cloudtask-api:prod --name cloudtask` (use o target `prod` — a imagem `dev` não embute o código, espera volume)
  - Minikube: `eval $(minikube docker-env)` antes do `docker build`.
- [ ] Aplicar tudo: `kubectl apply -f infra/k8s/`.
- [ ] Documentar no `infra/k8s/README.md`:
  - Como criar o cluster.
  - Como construir/carregar a imagem.
  - Como acessar a API (port-forward ou NodePort).
  - Como ver logs (`kubectl logs`) e simular falha (`kubectl delete pod`) para observar o auto-healing.

### Comandos esperados
```bash
kind create cluster --name cloudtask
docker build --target prod -t cloudtask-api:prod .
kind load docker-image cloudtask-api:prod --name cloudtask
kubectl apply -f infra/k8s/
kubectl get pods -n cloudtask
kubectl port-forward -n cloudtask svc/cloudtask-api 8000:8000
```

### Critérios de aceite
- `kubectl get pods -n cloudtask` mostra ≥ 2 pods `Running`.
- `curl http://localhost:8000/health` responde após port-forward.
- Ao deletar um pod, o Kubernetes recria automaticamente (demonstração de auto-healing).
- README da pasta `infra/k8s/` está completo.

### Referências
- [ROADMAP.md — Aula 6](ROADMAP.md)
- Kind: <https://kind.sigs.k8s.io/>
- Minikube: <https://minikube.sigs.k8s.io/docs/>
- Kubernetes — conceitos: <https://kubernetes.io/docs/concepts/>

---

# Semana 4 — AWS Academy, ECR e EKS

## Aula 7 — Publicar a imagem Docker no Amazon ECR

**Branch:** `semana-04-eks-aws` · **Issue:** #7
**Labels:** `semana-4`, `aula-07`, `ecr`, `aws`, `docker`

### Objetivo didático
Mostrar como a imagem Docker construída localmente é enviada para um **registry na nuvem** (Amazon ECR), tornando-se acessível a clusters Kubernetes na AWS. Introduzir o conceito de registry sem aprofundar em CI/CD.

### Pré-requisitos
- Imagem Docker funcionando (Semana 1)
- AWS CLI v2 instalada (`aws --version`)
- Conta no AWS Academy / Learner Lab com credenciais ativas
- `aws configure` executado com Access Key, Secret e região

### Entregas (checklist)
- [ ] Criar o repositório no ECR (uma vez):
  ```bash
  aws ecr create-repository --repository-name cloudtask-api --region us-east-1
  ```
- [ ] Criar `scripts/build-and-push-ecr.sh` automatizando:
  1. `aws ecr get-login-password ... | docker login ...`
  2. `docker build -t cloudtask-api .`
  3. `docker tag cloudtask-api:latest <account>.dkr.ecr.<region>.amazonaws.com/cloudtask-api:latest`
  4. `docker push <account>.dkr.ecr.<region>.amazonaws.com/cloudtask-api:latest`
  - Variáveis `AWS_REGION` e `AWS_ACCOUNT_ID` devem vir do ambiente ou de argumentos.
- [ ] Tornar o script executável (`chmod +x scripts/build-and-push-ecr.sh`).
- [ ] Criar `docs/ecr-guide.md` explicando:
  - O que é um container registry.
  - Diferenças entre Docker Hub e ECR.
  - Autenticação via AWS CLI.
  - Como tagear e versionar imagens (`latest`, `v1`, SHA do commit).
  - Custos básicos do ECR.

> ❗ **Não usar CI/CD profundo (GitHub Actions, Jenkins) nesta aula.** O foco é a operação manual.

### Critérios de aceite
- Após rodar o script, a imagem aparece no ECR (`aws ecr list-images --repository-name cloudtask-api`).
- O script falha de forma clara se faltar variável obrigatória.
- `docs/ecr-guide.md` existe e descreve cada passo.

### Referências
- [ROADMAP.md — Aula 7](ROADMAP.md)
- ECR — guia: <https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html>

---

## Aula 8 — Deploy da aplicação no Amazon EKS

**Branch:** `semana-04-eks-aws` · **Issue:** #8
**Labels:** `semana-4`, `aula-08`, `eks`, `aws`, `kubernetes`

### Objetivo didático
Levar a aplicação para um cluster Kubernetes **gerenciado** (EKS), com alta disponibilidade, Load Balancer público e **HTTPS na borda** (configurado conceitualmente na Aula 4). Todo manifest vem **comentado explicando motivo, impacto e risco**.

### Pré-requisitos
- Imagem `cloudtask-api` publicada no ECR (Aula 7)
- AWS CLI v2 + `kubectl` + `eksctl`
- Cluster EKS acessível (`aws eks update-kubeconfig --name <cluster> --region <region>`)

### Entregas (checklist)

**1. Manifests base** em `infra/k8s/aws/`
- [OK] `deployment-eks.yaml` — imagem do ECR, **2+ réplicas**, `resources.requests/limits` simples.
  - `livenessProbe` → `/health` (não toca o banco).
  - `readinessProbe` → `/health/ready` (checa o PostgreSQL — criado na Aula 4).
- [OK] `service-loadbalancer.yaml` — Service `LoadBalancer` (cria ELB/NLB).
- [OK] `README.md` da pasta, passo a passo + **como destruir** ao final.

**2. HTTPS na borda — dois caminhos**

*Caminho ideal (conta/domínio próprios):*
- [ ] ALB Ingress com ACM:
  - `alb.ingress.kubernetes.io/certificate-arn: <ARN do ACM>`
  - `alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'`
  - `alb.ingress.kubernetes.io/ssl-redirect: '443'` (redirect na **borda**)

*Caminho Learner Lab (sem domínio):*
- [OK] Documentar a limitação (ACM exige DNS) e expor **HTTP no ELB**, com comentário "aqui entraria o ACM em produção real".
- [OK] Aluno já viu HTTPS funcionando localmente via **mkcert** (Aula 4) — entendimento coberto.

- [OK] Garantir pods recebendo `X-Forwarded-Proto`; `FORCE_HTTPS` coerente com o ambiente.

>>>>>>>>>>>>>>>**********FAZER EKS**********<<<<<<<<<<<<<<<<

### Decisões e riscos (devem aparecer comentados nos manifests)

| Decisão | Por quê | Impacto | Risco se ignorar |
| --- | --- | --- | --- |
| `ssl-redirect` no **ALB**, não no app | Redirect num só lugar | App fica simples | App redirecionar + probe HTTP interno = **loop → pod unhealthy** |
| `readinessProbe` em `/health/ready` | Só recebe tráfego se o banco responde | Rollout espera o DB | Probe em `/health` deixa pod receber tráfego com banco fora |
| `livenessProbe` em `/health` | Reinicia só se o processo travou | Auto-healing correto | Liveness no banco reinicia o pod por falha do DB (errado) |
| Cert no **ACM**, colado ao ALB | Grátis, auto-renova | Sem gestão de cert | Cert manual expira e derruba HTTPS |
| `t3.small`/`t3.medium`, 2 nós | Learner Lab tem teto de crédito | Custo baixo | Nós grandes/muitos queimam o crédito |

### Critérios de aceite
- Pods `Running` lendo a imagem do ECR.
- `/health` e `/health/ready` respondem via Service/Ingress.
- Caminho ideal: `https://` funciona e `http://` redireciona (301) para `https://`.
- README explica destruição dos recursos.

> ⚠️ **Custos:** EKS + ELB + EC2 cobram por hora **ligados**. Sempre `kubectl delete -f infra/k8s/aws/` e `eksctl delete cluster` ao terminar.

### Referências
- [ROADMAP.md — Aula 8](ROADMAP.md)
- AWS Load Balancer Controller (Ingress + ACM): <https://kubernetes-sigs.github.io/aws-load-balancer-controller/>
- EKS user guide: <https://docs.aws.amazon.com/eks/latest/userguide/>
- eksctl: <https://eksctl.io/>

---

# Semana 5 — Elasticidade, Cost Explorer, NoSQL leve e logs

## Aula 9 — Escalabilidade horizontal (HPA), teste de carga e custos AWS

**Branch:** `semana-05-custos-nosql-logs` · **Issue:** #9
**Labels:** `semana-5`, `aula-09`, `scaling`, `cost`, `aws`, `kubernetes`

### Objetivo didático
Demonstrar **elasticidade** com Horizontal Pod Autoscaler, simular carga e relacionar o consumo de recursos ao **custo na AWS** usando o Cost Explorer.

### Pré-requisitos
- Aplicação rodando no EKS (Aula 8)
- Metrics Server instalado no cluster (`kubectl top pods` deve funcionar)

### Entregas (checklist)
- [ ] Criar `infra/k8s/hpa.yaml`:
  - Alvo: o Deployment `cloudtask-api`.
  - Métrica: CPU.
  - `minReplicas: 2`, `maxReplicas: 5`.
  - `averageUtilization: 60%`.
- [ ] Criar `scripts/load-test-simple.py` usando `httpx` ou `requests`:
  - Dispara N requisições paralelas para `/health` ou `/tasks`.
  - Parâmetros via CLI: `--url`, `--concurrency`, `--duration`.
- [ ] Aplicar o HPA e observar com:
  ```bash
  kubectl get hpa -n cloudtask -w
  kubectl get pods -n cloudtask -w
  ```
- [ ] Criar `docs/cost-explorer.md`:
  - O que é o AWS Cost Explorer.
  - Como abrir e filtrar por serviço (EKS, EC2, ECR, S3...).
  - Como criar um **Budget** com alerta por e-mail.
- [ ] Criar `docs/aws-pricing-notes.md`:
  - Visão geral de pricing dos serviços usados na disciplina (S3, EC2, EKS, ECR, DynamoDB).
  - Dicas para reduzir custo em ambiente de estudo (destruir clusters, usar `t3.small`, S3 Standard-IA, etc.).

### Critérios de aceite
- Sob carga, o HPA escala o Deployment de 2 → mais réplicas; ao cessar a carga, escala de volta.
- `scripts/load-test-simple.py` roda com um único `python` (sem ferramentas externas obrigatórias).
- Os dois documentos em `docs/` estão completos.

### Referências
- [ROADMAP.md — Aula 9](ROADMAP.md)
- HPA: <https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/>
- AWS Cost Explorer: <https://aws.amazon.com/aws-cost-management/aws-cost-explorer/>

---

## Aula 10 — Eventos e logs com Amazon DynamoDB (e fallback local em JSON)

**Branch:** `semana-05-custos-nosql-logs` · **Issue:** #10
**Labels:** `semana-5`, `aula-10`, `dynamodb`, `aws`, `fastapi`

### Objetivo didático
Introduzir **NoSQL** (sem aprofundar), mostrando um caso de uso comum: registrar **eventos e logs** de alteração de tarefas. Manter um fallback local em JSON para alunos sem AWS.

### Pré-requisitos
- CRUD de tarefas funcionando (Semana 2)
- *(Opcional)* DynamoDB real na AWS ou DynamoDB Local em Docker

### Entregas (checklist)
- [ ] Criar `app/services/dynamodb_service.py` com duas implementações:
  - **Modo local:** lê/escreve um arquivo `LOCAL_EVENTS_FILE` (default `./local_events/events.json`).
  - **Modo dynamodb:** usa `boto3.resource('dynamodb')` para `put_item` / `scan`.
- [ ] Criar `app/api/routes_events.py`:
  - `POST /events` — cria um evento manualmente.
  - `GET /events` — lista os eventos (paginação simples opcional).
- [ ] Em `routes_tasks.py`, emitir um evento automático em **create / update / delete** de tarefas.
- [ ] Modelo do evento:
  ```text
  Event:
    - id           (str, UUID)
    - event_type   (str: task.created | task.updated | task.deleted)
    - task_id      (int)
    - message      (str)
    - created_at   (datetime ISO 8601)
  ```
- [ ] Adicionar `local_events/` ao `.gitignore` (já está).
- [ ] Documentar no `README.md` da branch como alternar entre os modos.

### Variáveis de ambiente
```
EVENT_STORE_MODE=local         # local | dynamodb
LOCAL_EVENTS_FILE=./local_events/events.json
DYNAMODB_TABLE_NAME=cloudtask-events
# DYNAMODB_ENDPOINT_URL=http://localhost:8001   # opcional p/ DynamoDB Local
```

### Critérios de aceite
- Com `EVENT_STORE_MODE=local`: criar uma tarefa gera entrada no JSON.
- Com `EVENT_STORE_MODE=dynamodb` e tabela criada: a entrada aparece no DynamoDB.
- `GET /events` retorna a lista corretamente em ambos os modos.

### Observações
> A intenção **não é virar especialista em NoSQL**. É mostrar:
> - Modelagem chave-valor simples.
> - Uso comum (logs/eventos) onde NoSQL é mais natural que SQL.
> - Como esses dados poderiam alimentar um Data Lake (ligação com a Aula 5).

### Referências
- [ROADMAP.md — Aula 10](ROADMAP.md)
- DynamoDB boto3: <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html>

---

# Semana 6 — CDK, LGPD, backup e entrega final

## Aula 11 — Infraestrutura como código com AWS CDK (Python)

**Branch:** `semana-06-cdk-final` · **Issue:** #11
**Labels:** `semana-6`, `aula-11`, `cdk`, `iac`, `aws`

### Objetivo didático
Apresentar **Infrastructure as Code (IaC)** usando AWS CDK em Python. Provisionar de forma simples os recursos básicos usados pela aplicação (S3, ECR, VPC opcional) sem invadir o escopo de DevOps/Terraform.

### Pré-requisitos
- Node.js 20+ e `npm i -g aws-cdk` (`cdk --version` ≥ 2)
- Python 3.11+ e `pip install aws-cdk-lib constructs`
- Credenciais AWS configuradas
- Conta com bootstrap CDK: `cdk bootstrap aws://<account>/<region>`

### Entregas (checklist)
- [ ] Criar a estrutura:
  ```text
  infra/cdk/
  ├── app.py
  ├── requirements.txt
  ├── cdk.json
  ├── stacks/
  │   ├── __init__.py
  │   ├── storage_stack.py     # bucket S3 para uploads
  │   ├── ecr_stack.py         # repositório ECR para a imagem
  │   └── network_stack.py     # VPC básica (opcional)
  └── README.md
  ```
- [ ] `storage_stack.py`: cria bucket S3 com versionamento habilitado e `RemovalPolicy.DESTROY` (didático).
- [ ] `ecr_stack.py`: cria repositório ECR `cloudtask-api` com `image_scan_on_push=True`.
- [ ] `network_stack.py` *(opcional)*: VPC com 2 subnets públicas e 2 privadas, NAT mínimo.
- [ ] `app.py`: instancia as stacks com nomes claros (`CloudtaskStorageStack`, etc.).
- [ ] `infra/cdk/README.md`:
  - Como instalar dependências.
  - `cdk bootstrap`, `cdk synth`, `cdk diff`, `cdk deploy`, `cdk destroy`.
  - **Aviso de custos** e instrução de destruir após a aula.
- [ ] Atualizar `docs/` (opcional) com nota sobre quando usar CDK vs Console vs Terraform.

> ⚠️ **Não use Terraform.** Não automatize toda a infraestrutura complexa (EKS via CDK não cabe no escopo).

### Critérios de aceite
- `cdk synth` gera CloudFormation sem erro.
- `cdk deploy` cria os recursos solicitados na AWS.
- `cdk destroy` remove tudo sem deixar resíduo cobrável.
- README da pasta `infra/cdk/` está claro e completo.

### Referências
- [ROADMAP.md — Aula 11](ROADMAP.md)
- AWS CDK v2 (Python): <https://docs.aws.amazon.com/cdk/v2/guide/home.html>
- API reference: <https://docs.aws.amazon.com/cdk/api/v2/python/>

---

## Aula 12 — Documentação final, checklist LGPD e entrega do projeto

**Branch:** `semana-06-cdk-final` · **Issue:** #12
**Labels:** `semana-6`, `aula-12`, `documentation`, `lgpd`, `security`

### Objetivo didático
Consolidar todo o SaaS construído ao longo das 12 aulas, produzir a documentação final, validar conformidade com LGPD e segurança, e preparar o relatório final do trabalho.

### Pré-requisitos
- Aulas 1 a 11 concluídas
- Toda a aplicação rodando ponta a ponta (local e/ou AWS)

### Entregas (checklist)

**Documentação final em `docs/`**
- [ ] `docs/final-architecture.md` — diagrama e descrição da arquitetura final:
  - FastAPI no EKS, lendo imagem do ECR.
  - PostgreSQL (RDS ou container).
  - S3 para uploads.
  - DynamoDB para eventos/logs.
  - CDK para infraestrutura.
- [ ] `docs/final-report-template.md` — template do relatório final do aluno (capa, sumário, objetivos, arquitetura, custos, lições aprendidas).
- [ ] `docs/lgpd-checklist.md`:
  - Dados pessoais coletados (quais? por quê?).
  - Base legal (LGPD).
  - Política de retenção.
  - Direitos do titular.
  - Criptografia em repouso e em trânsito.
  - Logs de acesso.
- [ ] `docs/deployment-checklist.md`:
  - Pré-deploy (variáveis, secrets, backup).
  - Deploy (CDK / ECR / EKS).
  - Pós-deploy (smoke test em `/health`, conferência de custos, monitoramento básico).
  - Rollback simples (`kubectl rollout undo`).

**README final**
- [ ] Atualizar o `README.md` da branch com:
  - Instruções completas para rodar local, com Docker, com Kubernetes local, na AWS.
  - Diagrama da arquitetura final.
  - Tabela de variáveis de ambiente consolidada.
  - Links para todos os documentos em `docs/`.

**Validações finais**
- [ ] Smoke test em todos os endpoints via Swagger.
- [ ] Confirmar que **nenhum segredo** foi commitado (`git grep -i "secret\|password"`).
- [ ] Confirmar que recursos AWS de teste foram destruídos (`cdk destroy`, `kubectl delete`, etc.).

### Critérios de aceite
- Os 4 documentos em `docs/` estão presentes e completos.
- README final permite que um aluno novo rode tudo do zero.
- Checklists LGPD, segurança e custos preenchidos.
- Relatório final pode ser exportado a partir do template.

### Referências
- [ROADMAP.md — Aula 12](ROADMAP.md)
- LGPD (lei): <http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709.htm>
- AWS Well-Architected: <https://aws.amazon.com/architecture/well-architected/>

---

## Regras gerais do projeto

- Cada etapa **funciona isoladamente** e é compatível com a anterior.
- Código **simples, didático, bem comentado**, adequado a alunos de ADS no meio do curso.
- Sempre que houver dependência AWS, **prover fallback local**.
- **Não usar Terraform** (CDK apenas na semana 6).
- **Não aprofundar CI/CD**.
- Sem Grafana / Prometheus.
- Sem autenticação complexa.
- Sem frontend avançado — **Swagger da FastAPI é a interface principal**.
- Foco: **Computação em Nuvem aplicada**.
