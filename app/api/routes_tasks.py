"""
Rotas CRUD de tarefas (``/tasks``) do CloudTask AI SaaS.

CRUD = Create, Read, Update, Delete — as quatro operações básicas sobre um
recurso. Aqui o recurso é a tarefa (:class:`app.db.models.Task`).

PADRÃO desta camada (ver :mod:`app.api`):
    * A rota só orquestra HTTP: recebe dados, chama o banco, devolve resposta.
    * A sessão de banco vem por injeção de dependência (``Depends(get_db)``).
    * Entrada/saída sempre via schemas Pydantic (nunca o model ORM direto).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Task
from app.db.schemas import TaskCreate, TaskRead, TaskUpdate
from app.services.dynamodb_service import get_event_store, new_event

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _emit_task_event(event_type: str, task: Task) -> None:
    """Registra evento de tarefa sem interromper o fluxo principal do CRUD.

    Em ambiente didático/local, queremos observar eventos mas não tornar o
    CRUD indisponível se o backend de eventos estiver fora. Por isso, erros
    aqui são tratados como best-effort.
    """
    try:
        event_store = get_event_store()
        event_store.put_event(
            new_event(
                event_type=event_type,
                task_id=task.id,
                message=f"Task {task.id} ({task.title}) -> {event_type}",
            )
        )
    except Exception:
        # Melhor esforço: não bloquear o CRUD por falha no store de eventos.
        return


def _get_task_or_404(task_id: int, db: Session) -> Task:
    """Busca uma tarefa pelo id ou lança 404.

    Função auxiliar usada por GET-um, PUT e DELETE para não repetir o mesmo
    bloco de "buscar e checar se existe".

    Args:
        task_id: Identificador da tarefa.
        db: Sessão de banco.

    Returns:
        Task: a tarefa encontrada.

    Raises:
        HTTPException: 404 quando não existe tarefa com aquele id.
    """
    task = db.get(Task, task_id)
    if task is None:
        # POR QUÊ 404 e não 500: "não encontrado" é uma resposta esperada,
        # não um erro do servidor. Devolver o status certo ajuda o cliente
        # a tratar o caso corretamente.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com id={task_id} não encontrada.",
        )
    return task


CREATE_DESCRIPTION = """\
Cria uma nova tarefa.

O corpo aceita `title` (obrigatório), `description`, `status` e `priority`.
Os campos `id`, `created_at` e `updated_at` **não** são enviados pelo cliente —
o banco os preenche.

```bash
curl -X POST http://localhost:8000/tasks \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Estudar Docker","priority":"high"}'
```
"""


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tarefa",
    description=CREATE_DESCRIPTION,
    response_description="Tarefa criada, já com id e datas.",
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """Cria e persiste uma nova tarefa.

    Returns:
        Task: a tarefa recém-criada (o FastAPI converte para ``TaskRead``).
    """
    task = Task(**payload.model_dump(exclude_none=True))
    db.add(task)
    db.commit()       # grava de fato no banco
    db.refresh(task)  # recarrega id/created_at/updated_at gerados pelo banco
    _emit_task_event("task.created", task)
    return task


@router.get(
    "",
    response_model=list[TaskRead],
    summary="Listar tarefas",
    description="Retorna todas as tarefas. Use `skip`/`limit` para paginar.",
    response_description="Lista de tarefas.",
)
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Task]:
    """Lista tarefas com paginação simples.

    Args:
        skip: Quantos registros pular (offset). Default 0.
        limit: Máximo de registros a retornar. Default 100.

    Returns:
        list[Task]: tarefas encontradas, ordenadas por id.
    """
    # POR QUÊ paginar: sem limite, listar uma tabela enorme pode esgotar a
    # memória e travar a API. limit/skip mantêm a resposta sob controle.
    stmt = select(Task).order_by(Task.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Obter tarefa por id",
    response_description="A tarefa solicitada.",
    responses={404: {"description": "Tarefa não encontrada."}},
)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    """Retorna uma tarefa pelo id (404 se não existir)."""
    return _get_task_or_404(task_id, db)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Atualizar tarefa",
    response_description="A tarefa após a atualização.",
    responses={404: {"description": "Tarefa não encontrada."}},
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> Task:
    """Atualiza campos de uma tarefa existente.

    Apenas os campos enviados no corpo são alterados (atualização parcial).
    Um corpo vazio é válido e retorna a tarefa sem mudanças.

    Returns:
        Task: a tarefa atualizada.
    """
    task = _get_task_or_404(task_id, db)

    # `exclude_unset=True`: pega só os campos que o cliente realmente enviou,
    # preservando os demais. RISCO de não usar: campos omitidos viriam como
    # None e apagariam dados existentes.
    changes = payload.model_dump(exclude_unset=True)
    for campo, valor in changes.items():
        setattr(task, campo, valor)

    db.commit()
    db.refresh(task)
    _emit_task_event("task.updated", task)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover tarefa",
    responses={404: {"description": "Tarefa não encontrada."}},
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Remove uma tarefa pelo id.

    Retorna ``204 No Content`` (sucesso sem corpo) — convenção REST para
    deleção bem-sucedida.
    """
    task = _get_task_or_404(task_id, db)
    _emit_task_event("task.deleted", task)
    db.delete(task)
    db.commit()
    # 204: não retornamos corpo. POR QUÊ: o recurso não existe mais, então não
    # há o que devolver. Retornar o objeto deletado confundiria o cliente.
