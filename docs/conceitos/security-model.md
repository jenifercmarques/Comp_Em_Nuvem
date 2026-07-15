# Modelo de segurança — IAM, MFA, criptografia e LGPD

Guia conceitual de segurança do CloudTask AI SaaS na AWS. Complementa
[`aws-networking.md`](aws-networking.md) (rede) e [`https-tls.md`](https-tls.md)
(transporte).

---

## 1. Responsabilidade compartilhada

A segurança na nuvem é **dividida**:

| Quem | Responsável por |
| --- | --- |
| **AWS** | segurança **DA** nuvem: data centers, hardware, rede física, hipervisor |
| **Você** | segurança **NA** nuvem: seus dados, IAM, Security Groups, patches da app, criptografia |

> Resumindo: a AWS protege a infraestrutura; **você** protege o que coloca nela.
> Deixar um bucket S3 público ou uma senha no código é **sua** responsabilidade.

---

## 2. IAM — quem pode fazer o quê

**IAM (Identity and Access Management)** controla **identidades** e
**permissões** na AWS.

| Conceito | O que é | Exemplo |
| --- | --- | --- |
| **Usuário** | uma pessoa/credencial | `aluno-joao` |
| **Grupo** | conjunto de usuários | `desenvolvedores` |
| **Role (papel)** | identidade **assumível** por serviços/usuários | `LabRole` (Learner Lab) |
| **Policy** | documento JSON com permissões | "pode ler do bucket X" |

### Princípio do menor privilégio

Dê **só** a permissão necessária. RISCO de dar `AdministratorAccess` a tudo:
uma credencial vazada vira controle total da conta.

### Roles para serviços (sem chave!)

Em produção, o pod no EKS **assume uma role** para acessar S3/DynamoDB. NÃO
colocamos `AWS_ACCESS_KEY_ID` no código nem no `.env`. POR QUÊ: a role entrega
credenciais **temporárias e rotativas** automaticamente — nada de chave fixa
para vazar.

> No **Learner Lab** você não cria roles novas; usa a **`LabRole`** pronta
> (ver `../praticas/00-setup-inicial-e-aws-academy.md`).

---

## 3. MFA — autenticação em duas etapas

**MFA (Multi-Factor Authentication)** exige um segundo fator (app autenticador,
chave física) além da senha. POR QUÊ: senha vazada sozinha não basta para
entrar. **Ative MFA** na sua conta AWS real (no Learner Lab é gerenciado pela
instituição).

---

## 4. Criptografia

| Estado do dado | Como protegemos | Exemplo no projeto |
| --- | --- | --- |
| **Em trânsito** | TLS/HTTPS | API atrás de HTTPS (ver `https-tls.md`) |
| **Em repouso** | criptografia no armazenamento | S3 (SSE), RDS (encryption at rest), EBS |

- **Em trânsito:** ninguém lê o tráfego no caminho (cliente ↔ ALB ↔ app).
- **Em repouso:** se alguém roubasse o disco físico, os dados estão cifrados.
  S3 e RDS oferecem isso com um clique (chave gerenciada pela AWS/KMS).

---

## 5. Gestão de segredos

Regras do projeto:

- ✅ Segredos vêm de **variáveis de ambiente** (`.env` em dev) ou **Secrets**
  (Kubernetes/AWS em prod).
- ✅ `.env` está no `.gitignore`; só o `.env.example` (sem valores reais) é versionado.
- ❌ **Nunca** commitar senha, `SECRET_KEY`, access key. (Há um critério de
  aceite que roda `git grep -i "password\|secret" app/` para conferir.)
- 🔑 Gere o `SECRET_KEY` com:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

Se um segredo vazar: **rotacione imediatamente** (gere outro) e revise o
histórico do Git.

---

## 6. LGPD — Lei Geral de Proteção de Dados (Brasil)

A **LGPD** (Lei nº 13.709/2018) regula o tratamento de **dados pessoais**.
Mesmo um projeto didático deve pensar nisso desde o início ("privacy by design").

Perguntas que todo sistema deve responder (detalhamos na **Aula 12**):

| Pergunta | No CloudTask AI SaaS |
| --- | --- |
| Quais dados pessoais coletamos? | (hoje, nenhum sensível — só tarefas) |
| Qual a **base legal**? | consentimento / execução de contrato |
| Por quanto tempo guardamos? | política de retenção |
| Como o titular exerce direitos? | acesso, correção, exclusão |
| Os dados estão cifrados? | em trânsito (HTTPS) e em repouso (S3/RDS) |
| Há registro de acesso (logs)? | eventos na Aula 10 |

> Princípios-chave: **minimização** (colete só o necessário), **finalidade**
> (use só para o que foi informado) e **segurança** (proteja).

A AWS oferece recursos que **ajudam** na conformidade (criptografia, IAM, logs
com CloudTrail), mas a responsabilidade pelo **uso correto dos dados** é sua.

---

## 7. Checklist rápido de segurança (este projeto)

- [ ] Nenhum segredo no código/Git (`.env` ignorado).
- [ ] HTTPS na borda (ALB + ACM em prod).
- [ ] Banco em subnet privada, SG restrito.
- [ ] Menor privilégio no IAM (LabRole no lab).
- [ ] Criptografia em repouso ligada (S3/RDS).
- [ ] MFA na conta real.
- [ ] Logs de eventos (Aula 10) + revisão LGPD (Aula 12).

## Referências

- [`aws-networking.md`](aws-networking.md) · [`https-tls.md`](https-tls.md)
- AWS Well-Architected — Segurança: <https://aws.amazon.com/architecture/well-architected/>
- LGPD (texto da lei): <http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709.htm>
