# HTTPS e TLS no CloudTask AI SaaS

Guia didático de como deixamos a API segura no transporte (HTTPS), por que
fazemos as escolhas que fazemos, e o que cada uma impacta.

> **Resumo de uma frase:** o **app fala HTTP**; quem fala **HTTPS é a borda**
> (um Load Balancer na nuvem, ou um proxy/mkcert no seu PC).

---

## 1. O que é TLS/HTTPS (rápido)

- **HTTP** trafega em texto puro — qualquer um no caminho lê/altera.
- **HTTPS** = HTTP dentro de um túnel **TLS** (criptografado e autenticado).
- Para o TLS funcionar, é preciso um **certificado** assinado por uma
  autoridade (CA) em que o navegador confia.

---

## 2. Onde o TLS "termina"

"Terminar o TLS" = o ponto onde o tráfego criptografado é decifrado.

| Opção | Onde | Usamos? |
| --- | --- | --- |
| No app (uvicorn `--ssl-*`) | dentro do container | ❌ só demo local |
| Em um proxy (nginx/traefik/caddy) | na frente do app | ⚪ opcional |
| **No Load Balancer / Ingress (ALB)** | borda da nuvem | ✅ **produção (Aula 8)** |

**Decisão:** terminamos na **borda (ALB)**. O app recebe HTTP simples dentro da
rede privada. POR QUÊ: o ALB é gerenciado, escala, e integra com o certificado
da AWS (ACM) que **renova sozinho**.

---

## 3. Quem assina o certificado

| Ambiente | Emissor | Custo | Renovação | Aviso no browser? |
| --- | --- | --- | --- | --- |
| Dev local | **mkcert** (CA local) | grátis | manual | ❌ não (mkcert instala a CA) |
| Dev local | self-signed (openssl) | grátis | manual | ⚠️ sim |
| **Produção (ALB/CloudFront)** | **AWS Certificate Manager (ACM)** | grátis | **automática** | ❌ não |
| Produção (Ingress genérico) | Let's Encrypt (cert-manager) | grátis | automática | ❌ não |

> O certificado do **ACM vive colado ao ALB** — não dá para "baixar" e colocar
> dentro da imagem. Por isso o cert fica na borda, não no container.

---

## 4. Redirect HTTP → HTTPS

Queremos que quem acessar `http://` seja levado para `https://`.

- **Em produção:** o **ALB** faz o redirect (regra de listener `80 → 443`,
  anotação `alb.ingress.kubernetes.io/ssl-redirect: '443'`). É **uma linha** e
  vale para tudo.
- **No app:** só ligamos o `HTTPSRedirectMiddleware` no caso **raro** de o app
  estar exposto direto, **sem** proxy (`FORCE_HTTPS=true` e `BEHIND_PROXY=false`).

> 🔴 **Risco que evitamos:** se o app redirecionasse **atrás do ALB**, as
> *health probes* do Kubernetes (que chegam em HTTP interno) virariam um
> **loop de redirect** e o pod seria marcado como `unhealthy`. Por isso a
> guarda `and not settings.behind_proxy` em `app/main.py`.

---

## 5. Como o app "sabe" que está atrás de HTTPS

O ALB decifra o HTTPS e repassa HTTP ao pod, mas adiciona o cabeçalho
`X-Forwarded-Proto: https`. Para o uvicorn confiar nesse cabeçalho (e gerar
URLs/redirects corretos), subimos com:

```bash
uvicorn app.main:app --proxy-headers --forwarded-allow-ips='*'
```

Isso já está no `CMD` do `Dockerfile` (dev e prod). Sem `--proxy-headers`, o
app acharia que tudo é HTTP → risco de **loop de redirect** e links errados.

---

## 6. HSTS (Strict-Transport-Security)

Cabeçalho que diz ao navegador: "deste domínio, **sempre** use HTTPS por X
segundos". Enviado por `app/main.py` quando `FORCE_HTTPS=true` **e** o ambiente
não é `development`.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

> 🔴 **Sem `preload`.** A flag `preload` coloca o domínio numa lista embutida
> nos navegadores e é **praticamente irreversível** (fica meses). Em projeto
> de ensino, não usamos.
>
> ⚠️ **Nunca em `localhost`:** HSTS em dev travaria seus testes em HTTP. Por
> isso só enviamos fora de `development`.

---

## 7. As variáveis de ambiente (resumo)

| Variável | Dev (local) | Produção (EKS) | Efeito |
| --- | --- | --- | --- |
| `FORCE_HTTPS` | `false` | `true` | liga HSTS (e redirect no app se sem proxy) |
| `BEHIND_PROXY` | `true` | `true` | redirect é do ALB, não do app |
| `TRUSTED_HOSTS` | `*` | domínio real | rejeita Host header forjado |

---

## 8. HTTPS local com mkcert (opcional)

Para *ver* HTTPS funcionando na sua máquina sem aviso de browser:

```bash
# 1. instalar mkcert (uma vez) e a CA local
#    Windows:  winget install FiloSottile.mkcert
#    macOS:    brew install mkcert
mkcert -install

# 2. gerar cert para localhost
mkcert localhost 127.0.0.1

# 3. subir o uvicorn com TLS (apenas em dev!)
uvicorn app.main:app --host 0.0.0.0 --port 8443 \
  --ssl-keyfile localhost-key.pem --ssl-certfile localhost.pem
```

Acesse `https://localhost:8443/docs` — cadeado verde, sem aviso. POR QUÊ mkcert
e não openssl: o mkcert instala uma CA local em que o seu navegador confia, então
não aparece o aviso "conexão não segura".

> Isso é **só para aprender**. Em produção o TLS é do ALB + ACM (Aula 8).

---

## 9. Os dois caminhos na AWS Academy (Aula 8)

- **Ideal (conta/domínio próprios):** ACM + domínio + ALB Ingress + `ssl-redirect`.
- **Learner Lab (sem domínio):** ACM exige DNS → provavelmente indisponível.
  Demonstramos HTTPS localmente (mkcert) e, no EKS, expomos HTTP no ELB com um
  comentário "aqui entraria o ACM em produção real". O **entendimento** fica
  coberto sem depender de domínio.

## Referências

- [`security-model.md`](security-model.md) — IAM, MFA, criptografia, LGPD.
- AWS ACM: <https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html>
- mkcert: <https://github.com/FiloSottile/mkcert>
- Starlette middlewares: <https://www.starlette.io/middleware/>
