# Prática 08 — Debug com breakpoints no VS Code

> **Objetivo:** parar a execução em pontos específicos do código, inspecionar
> variáveis, navegar passo-a-passo. **Sem `print()` espalhado.**
>
> **Tempo:** 20 min.
>
> **Pré-req:** API rodando no devcontainer (ver [01](01-rodar-api-devcontainer.md)).

---

## Duas estratégias

A API já sobe sozinha no devcontainer com `uvicorn --reload`. Para debugar:

| Estratégia | Quando usar |
| --- | --- |
| **A — Attach com debugpy** | Quer manter o servidor rodando como está; debugar requests em tempo real |
| **B — Run com VS Code** | Quer controle total da execução; substitui o uvicorn auto |

Aqui ensinamos a **estratégia A** (mais didática — não precisa parar nada).

---

## 1. Confirmar que `debugpy` está instalado

Já vem no `requirements-dev.txt`. Para confirmar:

```bash
pip show debugpy
```

A porta `5678` já está exposta pelo `devcontainer.json`:
```json
"forwardPorts": [8000, 5678]
```

---

## 2. Patchar o `app/main.py` para aceitar debugpy

Adicione no **topo** de `app/main.py` (e remova ao terminar):

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
print("⏳ Aguardando debugger em 0.0.0.0:5678 ...")
debugpy.wait_for_client()  # opcional: bloqueia até VS Code conectar
```

> ⚠️ **NUNCA commitar** isso. Use só localmente. Em produção causaria
> deadlock e expor `5678` é risco de segurança.

> 💡 Alternativa elegante: `python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --reload`
> (sem mexer no código). Para isso, mude o `CMD` do Dockerfile dev temporariamente
> ou rode manualmente após `docker compose stop api`.

---

## 3. Configurar o VS Code (já tem `launch.json`)

O projeto tem `.claude/launch.json` ou `.vscode/launch.json` configurado com:

```json
{
  "name": "Python: Attach (debugpy)",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 },
  "pathMappings": [
    {
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/app"
    }
  ]
}
```

> `pathMappings` é crucial: os arquivos no seu disco estão em
> `workspaceFolder` mas dentro do container ficam em `/app`. Sem o mapping,
> os breakpoints não "casam".

---

## 4. Pôr um breakpoint

Abra `app/api/routes_tasks.py`. Clique na **margem esquerda** ao lado do
número de uma linha dentro de `create_task` — aparece bolinha vermelha 🔴.

Boa linha pra testar: a linha do `db.commit()` ou do `return task`.

---

## 5. Iniciar o attach

1. No VS Code, **Run and Debug** (ícone do play+inseto, Ctrl+Shift+D).
2. Escolha **Python: Attach (debugpy)** no dropdown.
3. Clique no **play verde**.

Status bar fica **laranja** → conectado.

---

## 6. Disparar a request

Em outro terminal:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Debug me"}'
```

**VS Code para no breakpoint.** Você verá:

- **Variables** (lado esquerdo) — `task`, `db`, `task_data`, etc.
- **Watch** — adicione `task.title`, `task.priority`.
- **Call Stack** — caminho de funções até aqui.
- **Debug toolbar** (topo):
  - Continue (F5)
  - Step Over (F10) — próxima linha
  - Step Into (F11) — entra na função
  - Step Out (Shift+F11) — sai da função

---

## 7. Inspecionar / mudar variáveis

- Passe o mouse sobre uma variável no código → tooltip com valor.
- Painel **Debug Console** (terminal embaixo): rode Python ao vivo.

  ```python
  task.title
  # 'Debug me'
  task.title = "Hackeado"
  # próxima linha vai salvar com este valor!
  ```

---

## 8. Continuar

`F5` → execução segue. O curl recebe a resposta. Você pode disparar outro
curl para parar de novo.

---

## 9. Sair / limpar

1. **Stop** (quadrado vermelho na debug toolbar) ou desconecte.
2. **Remova as 3 linhas** de debugpy do `app/main.py`.
3. Salve — o `--reload` recarrega sozinho.

---

## Bônus — debugar **testes**

`.vscode/launch.json` (ou adicione):

```json
{
  "name": "Python: Pytest current file",
  "type": "debugpy",
  "request": "launch",
  "module": "pytest",
  "args": ["${file}", "-v"],
  "console": "integratedTerminal",
  "justMyCode": false
}
```

Abra um `tests/test_*.py`, ponha breakpoint, escolha esse launch, F5.

---

## Erros comuns

| Erro | Causa | Fix |
| --- | --- | --- |
| Debug attach trava em "Waiting for connection" | porta 5678 ocupada / não exposta | confira `forwardPorts: [8000, 5678]` |
| Breakpoint fica **vazado** (bolinha branca) | `pathMappings` errado | `localRoot` = `${workspaceFolder}`, `remoteRoot` = `/app` |
| Breakpoint nunca dispara | request não chega na linha (rota errada) | confira URL e método no curl |
| `debugpy.wait_for_client()` trava a API | flag bloqueante | remova essa linha; mantenha só `listen` |

---

## Próximo passo

→ [`99-troubleshooting.md`](99-troubleshooting.md): catálogo de erros + fixes.
