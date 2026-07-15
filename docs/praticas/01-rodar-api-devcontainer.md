# Prática 01 — Rodar a API no devcontainer

> **Objetivo:** abrir o projeto no VS Code, subir o devcontainer e confirmar que
> a API está respondendo em `http://localhost:8000/docs`.
>
> **Tempo estimado:** 10 a 25 min (na primeira vez; depois é instantâneo).
>
> **Pré-requisitos:** [`00-setup-inicial-e-aws-academy.md`](00-setup-inicial-e-aws-academy.md)
> (Docker Desktop instalado e rodando, VS Code com extensão **Dev Containers**).

---

## 1. Garantir que o Docker está rodando

Antes de qualquer coisa:

```bash
docker --version
docker info
```

- `docker --version` deve mostrar versão (`Docker version 27.x...`).
- `docker info` deve listar `Server: ... Operating System: ...` SEM erro
  `Cannot connect to the Docker daemon`.

**Se der erro:** abra o **Docker Desktop** e espere o ícone parar de animar.

---

## 2. Estar na pasta certa, na branch certa

```bash
cd "caminho/da/pasta/CloudTask AI SaaS"

git branch --show-current
# saída esperada: semana-03-s3-kubernetes  (ou main, ou outra branch ativa)

git pull
```

---

## 3. Abrir no VS Code

```bash
code .
```

> 💡 **Aviso de pop-up:** "Folder contains a Dev Container configuration file.
> Reopen in container?" — clique **Reopen in Container**.

Se não apareceu o pop-up:

- `F1` → digite **Dev Containers: Reopen in Container** → Enter.

---

## 4. Esperar o build (primeira vez é lenta)

VS Code vai:

1. Baixar imagens base (Python 3.11-slim, postgres:16).
2. Instalar as **features** (zsh, AWS CLI, kubectl, docker CLI).
3. Rodar o **post-create** (eksctl, CDK, zsh plugins, permissions).
4. Subir `api` + `db` via `docker-compose.yml`.

> 🕒 **Pode levar 5 a 15 min na primeira vez.** Depois fica em cache; rebuild
> só dura ~1 min.

Quando estiver pronto, o terminal integrado abre como **zsh** com o prompt:
```
[2026-XX-XX HH:MM:SS] >
```

---

## 5. Confirmar que a API subiu

No terminal **dentro** do devcontainer:

```bash
curl -i http://localhost:8000/health
```

Resposta esperada:

```
HTTP/1.1 200 OK
content-type: application/json
{"status":"ok"}
```

**Outro teste rápido:**

```bash
curl http://localhost:8000/
# {"name":"CloudTask AI SaaS","version":"0.3.0","docs":"/docs"}
```

---

## 6. Abrir o Swagger no navegador

No seu navegador (no host, não dentro do container):

- <http://localhost:8000/docs> — Swagger UI
- <http://localhost:8000/redoc> — visão alternativa
- <http://localhost:8000/openapi.json> — spec OpenAPI bruto

> O VS Code faz o **port forwarding** automaticamente (porta 8000). Você vê
> isso no painel **PORTS** dele.

---

## 7. Parar a API (sem fechar o VS Code)

```bash
docker compose stop api
```

E para subir de novo:

```bash
docker compose start api
```

Para **derrubar tudo** (api + db) e liberar recursos:

```bash
docker compose down
```

---

## 8. Sair do devcontainer

`F1` → **Dev Containers: Reopen Folder Locally**.

Ou simplesmente feche o VS Code — `shutdownAction: stopCompose` no
`devcontainer.json` derruba os containers automaticamente.

---

## Erros comuns

| Erro | Causa provável | Fix |
| --- | --- | --- |
| `port is already allocated` | Outro Postgres/API ocupando 8000 ou 5432 | Pare o conflitante OU edite `.env` (`POSTGRES_PORT=5433`) |
| `Cannot connect to the Docker daemon` | Docker Desktop fechado | Abra o Docker Desktop |
| `ModuleNotFoundError: No module named 'boto3'` ao trocar de branch | Imagem antiga da branch anterior | `F1 → Dev Containers: Rebuild Container` |
| Swagger não carrega (`/docs` 404) | API ainda subindo | Aguarde 5–10s; `docker compose logs -f api` |
| 70 arquivos aparecem como "modified" | CRLF/fileMode entre Windows ↔ Linux | Já tratado por `.gitattributes` + post-create. Se acontecer: `git rm --cached -rf . && git reset --hard` |

---

## Próximo passo

→ [`02-explorar-swagger.md`](02-explorar-swagger.md): brincar com o Swagger UI.
