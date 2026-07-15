from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


HEALTH_DESCRIPTION = """\
Indica se o **processo da API está vivo**.

Endpoint leve e sem dependências externas, projetado para ser chamado por
orquestradores (Docker, Kubernetes, Load Balancers) **milhares de vezes
por dia** sem custo perceptível.

### Quando usar

| Consumidor | Configuração |
| --- | --- |
| Docker | `HEALTHCHECK` no `Dockerfile` |
| Kubernetes | `livenessProbe.httpGet.path: /health` |
| AWS ELB/ALB | Target Group Health Check Path = `/health` |

> <kbd>Importante</kbd> — esta rota **não** valida banco ou serviços
> externos. Para um check "está pronto para receber tráfego?", aguarde o
> endpoint `GET /health/ready` que será adicionado na Aula 3.

### Exemplos de uso

**curl**

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

**Python (httpx)**

```python
import httpx

resposta = httpx.get("http://localhost:8000/health")
assert resposta.status_code == 200
assert resposta.json() == {"status": "ok"}
```

**Manifest Kubernetes (trecho)**

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20
```
"""


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe da aplicação",
    description=HEALTH_DESCRIPTION,
    response_description="Estado do processo da API.",
    responses={
        200: {
            "description": "Aplicação viva e respondendo.",
            "content": {
                "application/json": {
                    "example": {"status": "ok"},
                }
            },
        },
    },
)
def health() -> HealthResponse:
    """Indica se o processo da API está vivo.

    Returns:
        HealthResponse: Objeto contendo ``status == "ok"`` quando o
        processo Python responde corretamente a requisições HTTP.

    Example:
        >>> health().status
        'ok'
    """
    return HealthResponse(status="ok")


READY_DESCRIPTION = """\
Indica se a aplicação está **pronta para receber tráfego** (readiness probe).

Diferente de `/health` (liveness), este endpoint **verifica dependências
externas**: nesta versão, executa um `SELECT 1` no **PostgreSQL**.

| Resultado | HTTP | Quando |
| --- | --- | --- |
| `{"status":"ready","db":"ok"}` | **200** | Banco respondeu |
| `{"status":"not_ready","db":"down"}` | **503** | Banco fora/inacessível |

### Por que separar de `/health`

| Probe | Endpoint | Se falhar, o Kubernetes... |
| --- | --- | --- |
| **liveness** | `/health` | **reinicia** o pod (processo travou) |
| **readiness** | `/health/ready` | **tira o pod do balanceador** até voltar |

> <kbd>Cuidado</kbd> — readiness toca o banco; liveness **não**. Se o liveness
> dependesse do banco, uma instabilidade do DB reiniciaria todos os pods sem
> necessidade.

```bash
curl -i http://localhost:8000/health/ready
```
"""


@router.get(
    "/health/ready",
    response_model=ReadyResponse,
    summary="Readiness probe (checa o PostgreSQL)",
    description=READY_DESCRIPTION,
    response_description="Estado de prontidão da aplicação.",
    responses={
        200: {
            "description": "Pronta: banco respondeu.",
            "content": {"application/json": {"example": {"status": "ready", "db": "ok"}}},
        },
        503: {
            "description": "Indisponível: banco fora.",
            "content": {
                "application/json": {"example": {"status": "not_ready", "db": "down"}}
            },
        },
    },
)
def ready(db: Session = Depends(get_db)) -> Response:
    """Verifica a conexão com o banco e responde 200 (pronto) ou 503 (não pronto).

    Args:
        db: Sessão de banco injetada pelo FastAPI.

    Returns:
        Response: ``200`` com ``ReadyResponse`` quando o banco responde;
        ``503`` (JSON) quando a consulta falha.
    """
    try:
        # SELECT 1 é a consulta mais barata possível: só confirma que o banco
        # aceita conexões e responde. Não lê nenhuma tabela.
        db.execute(text("SELECT 1"))
    except Exception:
        # POR QUÊ 503 (e não 500): "ainda não estou pronto" é diferente de
        # "deu erro interno". O 503 sinaliza ao balanceador para não mandar
        # tráfego para este pod até ele se recuperar.
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ReadyResponse(status="not_ready", db="down").model_dump(),
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ReadyResponse(status="ready", db="ok").model_dump(),
    )
