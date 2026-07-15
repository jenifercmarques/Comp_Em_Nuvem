"""Serviço de eventos com fallback local JSON ou DynamoDB.

Aula 10: queremos registrar eventos de domínio (create/update/delete de task)
sem depender obrigatoriamente da AWS. Por isso há dois modos:

* ``local``: grava em arquivo JSON (``LOCAL_EVENTS_FILE``)
* ``dynamodb``: grava em tabela DynamoDB (``DYNAMODB_TABLE_NAME``)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from app.core.config import settings


class EventStoreError(Exception):
    """Erro genérico do backend de eventos."""


class EventStoreBackend(Protocol):
    """Contrato comum para backends de eventos."""

    def put_event(self, event: dict[str, Any]) -> dict[str, Any]:
        ...

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        ...


def new_event(*, event_type: str, task_id: int | None, message: str) -> dict[str, Any]:
    """Cria payload de evento padronizado."""
    return {
        "id": str(uuid4()),
        "event_type": event_type,
        "task_id": task_id,
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


class LocalEventStore:
    """Armazena eventos em arquivo JSON local."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        self.file_path = Path(file_path or settings.local_events_file)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []
        try:
            content = self.file_path.read_text(encoding="utf-8")
            if not content.strip():
                return []
            data = json.loads(content)
            if not isinstance(data, list):
                raise EventStoreError("Arquivo de eventos local possui formato invalido.")
            return data
        except json.JSONDecodeError as exc:
            raise EventStoreError(f"Falha ao ler JSON local de eventos: {exc}") from exc

    def _write_all(self, events: list[dict[str, Any]]) -> None:
        self.file_path.write_text(
            json.dumps(events, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def put_event(self, event: dict[str, Any]) -> dict[str, Any]:
        events = self._read_all()
        events.append(event)
        self._write_all(events)
        return event

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        events = self._read_all()
        events.sort(key=lambda e: e.get("created_at", ""), reverse=True)
        return events[:limit]


class DynamoDBEventStore:
    """Armazena eventos em tabela DynamoDB."""

    def __init__(
        self,
        *,
        table_name: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.table_name = table_name or settings.dynamodb_table_name
        self.region = region or settings.aws_region
        self.endpoint_url = endpoint_url if endpoint_url is not None else settings.dynamodb_endpoint_url

    def _table(self):  # type: ignore[no-untyped-def]
        import boto3

        kwargs: dict[str, Any] = {"region_name": self.region}
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        resource = boto3.resource("dynamodb", **kwargs)
        return resource.Table(self.table_name)

    @staticmethod
    def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(item)
        if isinstance(normalized.get("task_id"), Decimal):
            normalized["task_id"] = int(normalized["task_id"])
        return normalized

    def put_event(self, event: dict[str, Any]) -> dict[str, Any]:
        try:
            self._table().put_item(Item=event)
            return event
        except Exception as exc:  # noqa: BLE001
            raise EventStoreError(f"Falha ao gravar evento no DynamoDB: {exc}") from exc

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        try:
            response = self._table().scan(Limit=limit)
            items = [self._normalize_item(i) for i in response.get("Items", [])]
            items.sort(key=lambda e: e.get("created_at", ""), reverse=True)
            return items
        except Exception as exc:  # noqa: BLE001
            raise EventStoreError(f"Falha ao listar eventos do DynamoDB: {exc}") from exc


def get_event_store() -> EventStoreBackend:
    """Seleciona backend de eventos conforme ``EVENT_STORE_MODE``."""
    if settings.event_store_mode == "dynamodb":
        return DynamoDBEventStore()
    return LocalEventStore()


__all__ = [
    "DynamoDBEventStore",
    "EventStoreBackend",
    "EventStoreError",
    "LocalEventStore",
    "get_event_store",
    "new_event",
]
