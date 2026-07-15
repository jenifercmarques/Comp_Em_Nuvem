# Prática 04 — Explorar o banco com psql

> **Objetivo:** conectar ao PostgreSQL **dentro do container `db`** e ver/manipular
> as tabelas direto via SQL. Útil para confirmar o que a API persistiu, debugar
> e entender o schema.
>
> **Tempo:** 15 min.
>
> **Pré-req:** Compose rodando (`docker compose ps` mostra `db` `Up (healthy)`).

---

## 1. Conectar no `psql`

No terminal do devcontainer (ou host com docker):

```bash
docker compose exec db psql -U cloudtask cloudtask
```

> 💡 Decompondo:
> - `docker compose exec db` — executa um comando dentro do container chamado `db`.
> - `psql` — cliente CLI do PostgreSQL.
> - `-U cloudtask` — usuário.
> - `cloudtask` (último) — nome do **banco** a conectar.

Você cai num prompt:

```
cloudtask=#
```

---

## 2. Comandos básicos do psql

| Comando | O que faz |
| --- | --- |
| `\l` | listar databases |
| `\dt` | listar tabelas |
| `\d tasks` | descrever tabela `tasks` (colunas, tipos, índices, constraints) |
| `\dn` | listar schemas |
| `\du` | listar usuários (roles) |
| `\q` | sair |
| `\?` | ajuda dos meta-comandos |
| `\h SELECT` | ajuda da sintaxe SQL `SELECT` |
| `\x` | toggle modo "expandido" (1 linha por campo, ótimo pra rows largas) |

---

## 3. Ver o schema da tabela `tasks`

```sql
\d tasks
```

Você verá algo como:

```
                                          Table "public.tasks"
    Column    |            Type             | ... | Default
--------------+-----------------------------+-----+--------------
 id           | integer                     | ... | nextval(...)
 title        | character varying(200)      | ... |
 description  | text                        | ... |
 status       | task_status (enum)          | ... |
 priority     | task_priority (enum)        | ... |
 created_at   | timestamp without time zone | ... | now()
 updated_at   | timestamp without time zone | ... | now()
Indexes:
    "tasks_pkey" PRIMARY KEY, btree (id)
```

> 💡 **Enums** vêm de `app/db/models.py` → `TaskStatus`, `TaskPriority`. O
> SQLAlchemy cria tipos enum nativos no Postgres a partir das classes Python.

---

## 4. Queries de exploração

**Contar tarefas:**

```sql
SELECT COUNT(*) FROM tasks;
```

**Listar as 10 últimas criadas:**

```sql
SELECT id, title, status, priority, created_at
FROM tasks
ORDER BY id DESC
LIMIT 10;
```

**Agrupar por status:**

```sql
SELECT status, COUNT(*) FROM tasks GROUP BY status;
```

**Buscar por padrão (LIKE):**

```sql
SELECT id, title FROM tasks WHERE title ILIKE '%aprender%';
```

(`ILIKE` = case-insensitive.)

---

## 5. INSERT manual (criar tarefa direto no banco)

```sql
INSERT INTO tasks (title, description, status, priority)
VALUES ('Tarefa via SQL', 'Inserida com psql', 'pending', 'low')
RETURNING *;
```

> `RETURNING *` devolve a row criada (com `id` autogerado).

Agora consulte a API:

```bash
curl -s http://localhost:8000/tasks | jq '.[-1]'
```

A tarefa criada pelo SQL aparece — porque a API e o psql leem **o mesmo
banco** (mesmo container `db`).

---

## 6. UPDATE / DELETE

```sql
UPDATE tasks SET status = 'done' WHERE id = 1 RETURNING *;

DELETE FROM tasks WHERE id = 1 RETURNING id;
```

---

## 7. Transações — desfazer alteração de testes

```sql
BEGIN;
DELETE FROM tasks;          -- limpa tudo
SELECT COUNT(*) FROM tasks; -- 0
ROLLBACK;                   -- desfaz! nada foi commitado
SELECT COUNT(*) FROM tasks; -- voltou ao que era
```

> 💡 É exatamente este truque que a fixture de testes (`tests/conftest.py`)
> usa: abre transação, roda o teste, **rollback** no final. Nada vaza pro banco
> de dev.

---

## 8. Sair

```sql
\q
```

---

## Erros comuns

| Erro | Causa | Fix |
| --- | --- | --- |
| `could not connect to server: Connection refused` | container `db` não subiu | `docker compose up -d db` |
| `FATAL: password authentication failed for user "cloudtask"` | senha errada (alguém mudou `.env`) | confira `POSTGRES_PASSWORD` no `.env` |
| `psql: command not found` (no host) | psql só existe no container | use `docker compose exec db psql ...` |
| `relation "tasks" does not exist` | banco zerado e API não subiu ainda | suba a API uma vez; ela cria as tabelas no `lifespan` (`Base.metadata.create_all`) |

---

## Próximo passo

→ [`05-uploads-modo-local.md`](05-uploads-modo-local.md): testar `/uploads` com
storage **local**.
