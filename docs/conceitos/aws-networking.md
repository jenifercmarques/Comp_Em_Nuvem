# Rede na AWS — VPC, subnets, Security Groups e companhia

Guia conceitual (sem provisionar nada) dos blocos de rede que sustentam a
aplicação na nuvem. A ideia é entender **onde** cada peça do CloudTask AI SaaS
vai morar quando subir no EKS (Aula 8) e no CDK (Aula 11).

---

## 1. VPC — sua rede privada na AWS

**VPC (Virtual Private Cloud)** é uma rede isolada, só sua, dentro da AWS. Tudo
(servidores, banco, balanceador) vive dentro dela. Você define a faixa de IPs
(ex.: `10.0.0.0/16`).

> Analogia: a VPC é o **terreno cercado**; dentro dele você constrói as casas
> (recursos) e decide quem entra.

---

## 2. Subnets — pedaços da VPC

A VPC é dividida em **subnets** (sub-redes). Cada subnet fica em uma **zona de
disponibilidade** (AZ — um data center). Usar 2+ AZs dá **alta disponibilidade**.

| Tipo | Acesso à internet | O que colocar |
| --- | --- | --- |
| **Pública** | Sim (via Internet Gateway) | Load Balancer, bastion |
| **Privada** | Não direto (só saída via NAT) | App (pods EKS), **banco (RDS)** |

> 🔒 **Decisão de segurança:** o banco fica em subnet **privada** — não é
> acessível da internet. POR QUÊ: reduz drasticamente a superfície de ataque.
> Quem acessa o banco é só a aplicação, dentro da VPC.

```text
                         Internet
                            │
                   ┌────────┴─────────┐
                   │ Internet Gateway │
                   └────────┬─────────┘
        VPC 10.0.0.0/16     │
   ┌────────────────────────┼─────────────────────────┐
   │  Subnet pública        │       Subnet pública     │   (AZ-a / AZ-b)
   │  ┌──────────────┐      │     ┌──────────────┐     │
   │  │ Load Balancer│◄─────┴────►│ NAT Gateway  │     │
   │  └──────┬───────┘            └──────┬───────┘     │
   │         │ (HTTP interno)            │ (saída)     │
   │  ┌──────▼───────┐            ┌──────▼───────┐     │
   │  │ App (pods)   │            │ App (pods)   │     │  Subnets privadas
   │  │  + RDS       │            │  + RDS       │     │
   │  └──────────────┘            └──────────────┘     │
   └───────────────────────────────────────────────────┘
```

---

## 3. Internet Gateway (IGW) e NAT Gateway

- **Internet Gateway (IGW):** porta de entrada/saída da VPC para a internet.
  Recursos em subnet pública o usam para receber tráfego de fora.
- **NAT Gateway:** deixa recursos em subnet **privada** **saírem** para a
  internet (ex.: baixar pacotes, falar com APIs da AWS) **sem** serem
  acessíveis de fora.

> 💸 **Cuidado de custo:** o NAT Gateway **cobra por hora + por tráfego**.
> No Learner Lab, é um dos vilões do orçamento. Destrua quando não usar.

---

## 4. Security Groups (SG) — firewall por recurso

Um **Security Group** é um firewall virtual que envolve um recurso (ex.: o RDS,
o Load Balancer). Você define regras de **entrada** (inbound) e **saída**.

Exemplo do nosso projeto:

| Recurso | Regra inbound | Significado |
| --- | --- | --- |
| Load Balancer | `443` de `0.0.0.0/0` | HTTPS de qualquer lugar |
| App (pods) | `8000` **só do SG do LB** | só o LB fala com a app |
| RDS (banco) | `5432` **só do SG da app** | só a app fala com o banco |

> 🔒 **Padrão "menor privilégio":** cada camada só aceita conexão da camada
> anterior. Ninguém fala direto com o banco. RISCO de abrir `5432` para
> `0.0.0.0/0`: expõe o banco à internet inteira.

SGs são **stateful**: se a entrada é permitida, a resposta sai automaticamente.

---

## 5. Bastion host (host de salto)

Servidor pequeno em subnet **pública** usado para acessar (via SSH) recursos da
subnet **privada** quando necessário (ex.: depurar o banco).

> Em vez de expor o banco, você "salta" por um bastion controlado. Hoje muita
> gente usa o **AWS Systems Manager Session Manager** no lugar do bastion
> (sem porta SSH aberta) — mais seguro.

---

## 6. Como o CloudTask AI SaaS se encaixa

| Componente | Onde fica | Exposto à internet? |
| --- | --- | --- |
| Load Balancer (ALB) | subnet pública | Sim (HTTPS 443) |
| API FastAPI (pods EKS) | subnet privada | Não (só via LB) |
| PostgreSQL (RDS) | subnet privada | Não (só via app) |
| S3, DynamoDB | serviços gerenciados (fora da VPC) | acesso via IAM |

No **CDK (Aula 11)** criaremos uma VPC básica com essa estrutura (2 subnets
públicas + 2 privadas). No **Learner Lab**, muitas vezes já existe uma VPC
default — podemos reutilizá-la para economizar tempo e crédito.

---

## Referências

- [`security-model.md`](security-model.md) — IAM, MFA, criptografia, LGPD.
- [`https-tls.md`](https-tls.md) — TLS na borda (ALB).
- AWS VPC: <https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html>
