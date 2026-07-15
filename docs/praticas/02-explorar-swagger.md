# Prática 02 — Explorar o Swagger UI

> **Objetivo:** entender que o Swagger UI **não é só documentação**, é uma
> **interface real** que permite testar a API sem instalar nada (sem Postman,
> Insomnia, etc.).
>
> **Tempo:** 15 min.
>
> **Pré-req:** API rodando em `http://localhost:8000` (ver [01](01-rodar-api-devcontainer.md)).

---

## 1. Abrir o Swagger

Navegador → <http://localhost:8000/docs>.

O que você vê:

1. **Banner do topo** — descrição rica em Markdown (tabela de semanas, links,
   status). Definido em `app/main.py → APP_DESCRIPTION`.
2. **Tags coloridas** (meta, health, tasks, uploads) — agrupam endpoints por
   contexto. Cada tag tem descrição.
3. **Lista de endpoints** — clicáveis, expansíveis.
4. **Models** (fim da página) — schemas Pydantic (`TaskRead`, `TaskCreate`,
   `UploadResponse`, etc.).

---

## 2. Try it out — criar uma tarefa

1. Clique em **`POST /tasks`** (expande).
2. Clique no botão **Try it out** (canto direito).
3. O campo **Request body** vira editável. Cole:

   ```json
   {
     "title": "Estudar Swagger",
     "description": "Aula 2 — explorar try it out",
     "status": "pending",
     "priority": "medium"
   }
   ```

4. Clique **Execute**.

**Você verá:**

- **Curl** equivalente (copie-e-cole no terminal — Swagger gera pra você).
- **Request URL** real: `http://localhost:8000/tasks`.
- **Server response** — código `201 Created` + JSON com `id`, `created_at`, etc.

> 💡 **Por que isso é mágico?** O Swagger UI consome o `openapi.json` (que a
> FastAPI gera AUTOMATICAMENTE a partir dos seus type hints + schemas Pydantic)
> e renderiza um cliente HTTP completo.

---

## 3. Listar tarefas e ver paginação

`GET /tasks` → **Try it out** → preencha:

- `skip` = `0`
- `limit` = `5`

→ **Execute**.

Resposta: array com até 5 tarefas. Mude `skip=5` para pular as 5 primeiras.

> Paginação é controlada por **query parameters**. No curl seria
> `GET /tasks?skip=5&limit=5`. O Swagger te dá um formulário.

---

## 4. Inspecionar um schema (Pydantic → OpenAPI)

Role até o fim da página → seção **Schemas**.

Clique em `TaskRead`. Veja:

- Campos, tipos, descrições, exemplos.
- Tudo gerado a partir de `app/schemas.py`.

> O **mesmo schema** é usado: (1) para validar entrada (POST), (2) para
> serializar saída (response), (3) para gerar essa documentação. Uma fonte da
> verdade. Esse é o trunfo da FastAPI.

---

## 5. Provocar um erro de validação (422)

Em `POST /tasks` → Try it out → **mande um JSON inválido**:

```json
{
  "title": ""
}
```

→ **Execute**.

Resposta:

```
422 Unprocessable Entity
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      ...
    }
  ]
}
```

> ✅ **Sem você escrever validação manualmente.** Pydantic + FastAPI já fazem.

---

## 6. Baixar o OpenAPI bruto

Navegador → <http://localhost:8000/openapi.json>.

É um JSON enorme — o **contrato** da API. Pode ser:

- Importado no Postman.
- Usado para gerar **clients** (Python, TypeScript, Java...) com
  [openapi-generator](https://openapi-generator.tech/).
- Comparado entre versões (`v0.2.0` vs `v0.3.0`) pra detectar breaking changes.

---

## 7. ReDoc — visão alternativa

<http://localhost:8000/redoc>

Mesma documentação, layout diferente (3 colunas, mais legível para "ler",
menos para "testar"). Útil para distribuir como manual.

---

## Desafio (opcional)

1. Crie 3 tarefas via Swagger com `priority` diferentes.
2. Use `GET /tasks` para listar.
3. Atualize uma via `PUT /tasks/{id}` (mude `status` para `done`).
4. Apague outra via `DELETE /tasks/{id}` → resposta `204 No Content`.
5. Tente `GET /tasks/999999` → resposta `404` (com `detail`).

---

## Próximo passo

→ [`03-crud-tasks-via-curl.md`](03-crud-tasks-via-curl.md): mesmas operações,
mas pelo **terminal**.
