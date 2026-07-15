# Relatório final — CloudTask AI SaaS

> **Template de entrega**
---

## 1. Identificação

- **Aluno(a):** Jenifer Carvalho Marques
- **RU / matrícula:** 4958653
- **Disciplina:** Computação em Nuvem — UNINTER
- **Repositório:** link do seu fork/branch
- **Data:** 15/07/2026`

## 2. Resumo do projeto

O CloudTask AI SaaS e uma API para gerenciar tarefas com operacoes de criar, listar, atualizar e excluir.
O projeto foi desenvolvido com FastAPI, PostgreSQL e Docker, com testes automatizados para validar o funcionamento.
Tambem foi implementado upload de arquivos (modo local e S3) e registro de eventos (modo local e DynamoDB), mantendo foco em execucao simples e didatica.

## 3. O que foi implementado (por semana)

| Semana | Entreguei | Evidência (print / comando / endpoint) |
| --- | --- | --- |
| 1 — FastAPI + Docker | SIM | docs/evidencias/fast_api&Docker.png |
| 2 — PostgreSQL + config | SIM | docs/evidencias/PSQL.png & docs/evidencias/PSQL(1).png |
| 3 — S3 + Kind | SIM | docs/evidencias/S3 (1).png & docs/evidencias/S3 (2).png & docs/evidencias/kind.png |
| 4 — ECR + EKS | PARCIAL: ECR SIM, EKS NAO | docs/evidencias/ecr-push.png |
| 5 — HPA + DynamoDB | PARCIAL: HPA NAO, DynamoDB SIM | docs/evidencias/dynamo-events.png & docs/evidencias/dynamo-scan.png |
| 6 — CDK + entrega | NAO IMPLEMENTADO | sem evidencias de CDK |

## 4. Arquitetura

Cole/descreva a arquitetura. Pode reaproveitar o diagrama de
final-architecture.md e adaptar ao que VOCÊ subiu.

## 5. Como executar (reprodutível)

```bash
# 1) clonar o repositorio e entrar na pasta
git clone https://github.com/N-CPUninter/Computa-o-em-Nuvem---Projeto-exemplo-CloudTask-AI-SaaS.git
cd Computa-o-em-Nuvem---Projeto-exemplo-CloudTask-AI-SaaS

# 2) criar arquivo de configuracao local
cp .env.example .env

# 3) subir a aplicacao com Docker (API + banco)
docker compose up --build

# 4) testar no navegador
# Swagger: http://localhost:8000/docs
# Health:  http://localhost:8000/health

# 5) quando terminar, parar os containers
docker compose down
```

Observacoes simples:
- Este passo a passo cobre a execucao local com Docker, que foi a base usada no projeto.
- EKS, HPA e CDK nao foram implementados nesta entrega.

## 6. Decisões e trade-offs

- **PostgreSQL em container (local) em vez de RDS:** usei banco local para praticar sem custo extra. Trade-off: bom para estudo e reproducao, mas sem alta disponibilidade e sem recursos gerenciados da AWS.
- **Criacao de tabelas com `create_all`:** o projeto cria tabelas automaticamente no startup. Trade-off: simples para aprender, mas nao substitui migracoes versionadas em projeto real.
- **Configuracao centralizada com `.env` + Pydantic Settings:** as variaveis ficaram organizadas em um unico lugar. Trade-off: melhora seguranca e manutencao, mas exige mais cuidado inicial para configurar corretamente.
- **Uploads com dois modos (local e S3):** mantive fallback local para funcionar sem AWS e modo S3 para nuvem. Trade-off: aumenta flexibilidade para aula, mas duplica logica e exige testar os dois caminhos.
- **Eventos com fallback (JSON local ou DynamoDB):** eventos podem ser gravados localmente ou no DynamoDB. Trade-off: facilita estudar sem AWS, mas o modo local nao escala como banco NoSQL gerenciado.
- **Falha de eventos em modo "best effort":** se o registro de evento falhar, o CRUD de tarefas continua funcionando. Trade-off: melhora disponibilidade da API, mas pode perder eventos em caso de erro no backend de eventos.
- **Seguranca HTTP/HTTPS condicional por ambiente:** middleware de HTTPS e hosts confiaveis dependem da configuracao. Trade-off: evita problemas em desenvolvimento, mas exige configuracao correta em producao para nao abrir brechas.
- **Imagem Docker multi-target (dev/test/prod):** um Dockerfile atende varios cenarios. Trade-off: reduz duplicacao e padroniza, mas aumenta a complexidade do Dockerfile para quem esta iniciando.
- **Testes com rollback de transacao no mesmo banco:** cada teste limpa o que fez via transacao. Trade-off: testes ficam mais rapidos e estaveis, mas nao simulam isolamento completo com um banco separado so para testes.

Observacao de escopo desta entrega:
- EKS, HPA e CDK nao foram implementados como ambiente final em execucao; o foco ficou em API, banco, uploads, ECR e DynamoDB.

## 7. Custos

- Recursos que cobraram:
  - EC2 - Other: `US$ 0,01`
  - Virtual Private Cloud: `US$ 0,03`
  - EC2 - Compute: `US$ 0,07`
  - S3: `US$ 0,00`
  - CloudWatch: `US$ 0,00`
  - Outros: `US$ 0,07`
- Estimativa do período: `US$ 0,18`
- Observacao: os custos ocorreram mesmo sem implementacao final de EKS, HPA e CDK.

## 8. LGPD e segurança

- O checklist LGPD foi preenchido e os pontos principais foram atendidos na entrega: mapeamento dos dados, armazenamento, cuidado com segredos e uso de S3 privado.
- A API tambem possui caminhos para consultar e excluir dados.

## 9. Dificuldades e aprendizados

- A principal dificuldade foi configurar o ambiente no inicio (Docker, .env e conexao com PostgreSQL), porque pequenos erros de porta ou variavel impediam a API de subir. Resolvi revisando o arquivo .env, os logs do docker compose e os passos do guia de troubleshooting.
- Outra dificuldade foi alternar entre modo local e modo AWS (uploads e eventos), principalmente por causa de credenciais e comportamento diferente entre local e nuvem. Resolvi testando primeiro no modo local e depois ativando S3/DynamoDB com validacao por endpoint.
- O maior aprendizado foi entender o fluxo completo: API, banco, armazenamento e custos. Tambem aprendi que simplificar (fallback local, Docker Compose e checks de seguranca) ajuda a entregar com qualidade, mesmo sem implementar toda a parte de EKS, HPA e CDK.

## 10. Anexos

- [OK] `lgpd-checklist.md` preenchido
- [NO] `deployment-checklist.md` (sweep de limpeza) preenchido
- [OK] Prints / logs das evidências da seção 3