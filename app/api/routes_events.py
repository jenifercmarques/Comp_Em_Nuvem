"""Rotas de eventos (Aula 10).

``POST /events`` cria evento manualmente.
``GET /events`` lista eventos do backend configurado.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import EventCreate, EventRead
from app.services.dynamodb_service import EventStoreError, get_event_store, new_event

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar evento manual",
    description=(
        "Registra um evento no backend configurado em EVENT_STORE_MODE. "
        "Use para testes e para demonstrar modelagem NoSQL simples."
    ),
)
def create_event(payload: EventCreate) -> dict:
    event_store = get_event_store()
    event = new_event(
        event_type=payload.event_type,
        task_id=payload.task_id,
        message=payload.message,
    )
    try:
        return event_store.put_event(event)
    except EventStoreError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[EventRead],
    summary="Listar eventos",
    description="Retorna eventos do backend local JSON ou DynamoDB.",
)
def list_events(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    event_store = get_event_store()
    try:
        return event_store.list_events(limit=limit)
    except EventStoreError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
