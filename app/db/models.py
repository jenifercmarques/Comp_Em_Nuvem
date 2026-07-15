"""
Modelos ORM (tabelas do banco) do CloudTask AI SaaS.

Um "modelo" descreve **como o dado é guardado no banco**. Cada classe vira
uma tabela; cada atributo vira uma coluna. Não confunda com os *schemas*
(:mod:`app.db.schemas`), que descrevem **como o dado entra/sai pela API**.

Modelo desta aula: :class:`Task` (uma tarefa do nosso mini-SaaS).
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TaskStatus(str, enum.Enum):
    """Estados possíveis de uma tarefa.

    Herdar de ``str`` faz o valor ser serializado como texto simples no JSON
    (ex.: ``"pending"``), o que aparece bonito no Swagger e no banco.
    """

    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, enum.Enum):
    """Níveis de prioridade de uma tarefa."""

    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    """Tabela ``tasks`` — uma tarefa do CloudTask AI SaaS.

    Atributos:
        id: Chave primária autoincrementada.
        title: Título curto e obrigatório da tarefa.
        description: Texto livre opcional com detalhes.
        status: Estado atual (:class:`TaskStatus`). Default ``pending``.
        priority: Prioridade (:class:`TaskPriority`). Default ``medium``.
        created_at: Data/hora de criação (preenchida pelo banco).
        updated_at: Data/hora da última alteração (atualizada pelo banco).

    Notas de decisão:
        * ``created_at`` / ``updated_at`` usam ``server_default``/``onupdate``
          com ``func.now()`` — quem carimba a hora é o **banco**, não a
          aplicação. POR QUÊ: garante hora consistente mesmo com várias
          réplicas da API (Aula 8) rodando em relógios ligeiramente diferentes.
        * Usamos ``Enum`` nativo do PostgreSQL para status/priority. IMPACTO:
          o próprio banco recusa valores inválidos. RISCO de usar string
          livre: dados inconsistentes (ex.: "Pendente", "pendente", "PENDING").
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.pending,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority"),
        nullable=False,
        default=TaskPriority.medium,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representação curta para logs/depuração."""
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
