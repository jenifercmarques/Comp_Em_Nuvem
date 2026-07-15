# Arquitetura final — CloudTask AI SaaS

Visão consolidada do que a disciplina construiu, da máquina local à nuvem.

> Documento de **fechamento** (Aula 12). Resume as 6 semanas em um só lugar.

---

## Linha do tempo (o que cada semana somou)

| Semana | Camada adicionada | Tema |
| -----: | --- | --- |
| 1 | API FastAPI + Docker + devcontainer | base |
| 2 | PostgreSQL + CRUD + `.env` + HTTPS (conceito) | persistência + config |
| 3 | Uploads (S3 / local) + Kubernetes local (Kind) | storage + orquestração local |
| 4 | Imagem no ECR + deploy no EKS | nuvem (registry + cluster gerenciado) |
| 5 | HPA + custos + eventos (DynamoDB / JSON) | elasticidade + NoSQL |
| 6 | CDK (IaC, 7 stacks) + autenticação (JWT) + frontend SPA + 3 servidores EC2 (API/Front/Grafana) + entrega final | infra como código + segurança + consolidação |

---

## Arquitetura de produção (alvo final)

```text
                         Internet (HTTPS)
                              │
                       www.seu-dominio  ── Route 53 (DNS)
                              │
                         ┌────▼─────┐
                         │   ALB    │ ◄── ACM (certificado TLS)
                         └────┬─────┘
                  TLS termina aqui; HTTP interno
                              │
              ┌───────────────▼────────────────┐
              │        Amazon EKS (cluster)     │
              │   ┌──────────┐   HPA 2..5       │
              │   │ Pods API │ ◄── escala c/ CPU│
              │   └────┬─────┘                  │
              └────────┼───────────────────────┘
                       │
        ┌──────────────┼───────────────┬──────────────┐
        ▼              ▼               ▼              ▼
  RDS PostgreSQL   Amazon S3      DynamoDB        ECR (imagem)
  (tarefas)        (uploads)      (eventos/logs)  (origem do deploy)

  Infra descrita como código (CDK): S3, ECR, VPC  →  reprodutível e versionada.
```

> Esta é a topologia **alvo** (demonstrada na conta pessoal do professor, com
> domínio real). No Learner Lab, partes ficam simplificadas (sem Route53/ACM;
> Postgres pode rodar como Pod em vez de RDS).

### Topologia da Semana 6 — 3 servidores via CDK (o que de fato sobe no Lab)

Para mostrar IaC gerenciando uma infra **mais complexa**, a Aula 12 sobe **três
servidores separados** com **um Edge HTTPS na frente** (a 7ª stack do CDK,
`ComputeStack` — ver
[`infra/cdk/stacks/compute_stack.py`](../../infra/cdk/stacks/compute_stack.py)).
O **mesmo** resultado sai pelo script CLI
[`infra/servers/semana-06-servidores-subir.sh`](../../infra/servers/semana-06-servidores-subir.sh):

```text
  navegador ──HTTPS (cert válido)──► EDGE (Caddy)  ──HTTP interno──►  API EC2 (:8000)
  (443)                              <ip>.sslip.io  ├─ /api/*      ──►  FastAPI + JWT ──► RDS (5432)
                                     serve o SPA;    └─ /grafana/*  ──►  Grafana EC2 (:3000) ──► CloudWatch
                                     80→443; Swagger
                                     com senha
  (API e Grafana NÃO ficam expostos à internet — 8000/3000 só dentro do SG; só o Edge é público)
```

* **Edge (Caddy)** — Elastic IP + hostname `<ip>.sslip.io` → obtém um
  **certificado válido** (ACME/Let's Encrypt) sem domínio próprio; serve o SPA,
  faz proxy `/api`→API e `/grafana`→Grafana, redireciona 80→443 e protege o
  **Swagger com senha** (basic auth).
* **API** — FastAPI com **login JWT**; conecta no **RDS** (senha no Secrets
  Manager). Acessível só pelo Edge, em `/api`.
* **Grafana** — datasource CloudWatch (role do EC2, sem chave fixa) + dashboard
  como home, sob `/grafana`.

> 🧩 **Por que separar em vários servidores?** Não era obrigatório para a app
> funcionar — foi **de propósito**, para a infra ganhar mais peças (Edge HTTPS +
> API + Grafana: mais EC2, security group, Elastic IP, certificado, URLs). Quanto
> **mais complexa** a topologia, mais evidente fica o **ganho do CDK**: descrever
> Edge + API + Grafana + RDS + VPC + observabilidade como código e subir/derrubar
> com **um comando** é muito mais rápido, seguro e gerenciável do que
> clicar/scriptar na mão.

> 🔐 **Autenticação — o ideal vs. o que o Lab permite.** O **TLS/certificado já
> fica isolado no Edge** — o Caddy obtém e renova o cert; a API **nunca** toca
> certificado (essa é justamente a boa prática: terminar TLS na borda, não no
> app). O que **ainda** é simplificação: a **autenticação (JWT) roda no próprio
> backend**. Em produção de verdade usaríamos um **servidor de autenticação
> dedicado** (ex.: **Authentik**) falando OAuth2/OIDC, que centraliza
> login/usuários e isola a emissão de credenciais (um comprometimento do backend
> não deve levar junto o material de autenticação). Aqui, pelas **limitações do
> Lab** (sessão curta, sem domínio próprio), o JWT é emitido/validado no mesmo
> container da API. Funciona para a demo; o caminho "produção" é o servidor de
> auth separado.

---

## Componentes e responsabilidades

| Componente | Papel | Onde nasceu |
| --- | --- | --- |
| **FastAPI** | API REST + Swagger | Semana 1 |
| **PostgreSQL / RDS** | dados relacionais (tarefas) | Semana 2 / 6 |
| **Amazon S3** | arquivos (uploads), base de Data Lake | Semana 3 |
| **Kubernetes (Kind→EKS)** | orquestração de containers | Semanas 3–4 |
| **Amazon ECR** | registry da imagem da API | Semana 4 |
| **HPA** | escala automática de réplicas | Semana 5 |
| **DynamoDB** | eventos/logs (NoSQL) | Semana 5 |
| **ALB + ACM + Route 53** | borda HTTPS + domínio (no **alvo EKS**) | Semana 6 (alvo) |
| **Edge (Caddy) + SPA** | borda HTTPS **no Lab**: cert válido (ACME/sslip.io), proxy `/api` e `/grafana`, serve o SPA, redirect 80→443, Swagger com senha | Semana 6 |
| **Autenticação (JWT)** | login/token na API (Bearer); em prod, servidor dedicado (Authentik) | Semana 6 |
| **Grafana + CloudWatch** | observabilidade (dashboards), acessada via `/grafana` no Edge | Semana 6 |
| **AWS CDK (7 stacks)** | infra como código: S3, ECR, VPC, DynamoDB, CloudWatch/SNS, RDS, **Compute (3 EC2)** | Semana 6 |

---

## Decisões de projeto (e por quê)

- **Fallback local em tudo que depende de nuvem** (S3→disco, DynamoDB→JSON):
  o aluno completa as aulas **sem AWS**.
- **Imagem `prod` embute o código** (`COPY`), `dev` usa volume: cluster precisa
  de imagem autossuficiente.
- **Cada banco para seu uso:** SQL (tarefas) + NoSQL (eventos). Não é "um
  substitui o outro".
- **Custo é cidadão de primeira classe:** todo recurso caro tem aviso + roteiro
  de destruição.
- **Edge HTTPS na frente (de propósito):** além de adicionar uma peça à infra
  (evidenciando que o **CDK gerencia complexidade crescente** com o mesmo
  esforço), ele **termina o TLS na borda** — a API nunca administra certificado,
  e o mundo só fala com o Edge (menos superfície de exposição).
- **Autenticação no backend é simplificação do Lab:** o desenho de produção usa
  um **servidor de auth separado (Authentik)** para centralizar login e isolar a
  emissão de credenciais. No Lab, o JWT roda no mesmo container da API (o TLS,
  esse sim, já fica isolado no Edge).

---

## Para a entrega

- Preencha o [`final-report-template.md`](final-report-template.md).
- Rode o [`deployment-checklist.md`](deployment-checklist.md) antes de demonstrar.
- Confirme o [`lgpd-checklist.md`](lgpd-checklist.md).