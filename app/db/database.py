"""
Conexão com o banco de dados e gerência de sessões (SQLAlchemy).

Este módulo cria:
    * ``engine``       — o "motor" que sabe falar com o PostgreSQL.
    * ``SessionLocal`` — fábrica de sessões (uma sessão = uma conversa curta
      com o banco, geralmente uma requisição HTTP).
    * ``Base``         — classe-base de onde todos os modelos herdam.
    * :func:`get_db`   — dependência do FastAPI que entrega uma sessão e
      garante o fechamento dela ao fim da requisição.

----------------------------------------------------------------------------
POR QUÊ PostgreSQL (e não SQLite)?
    Queremos um banco igual ao de produção. Usamos **PostgreSQL 16**, que é
    exatamente uma das engines do **Amazon RDS**. Assim o mesmo `DATABASE_URL`
    serve para o container local (Aula 3) e para o RDS na nuvem (sem trocar
    código — só a variável de ambiente).

IMPACTO:
    O aluno aprende no mesmo banco que usaria em produção. Migrar para o RDS
    vira "trocar a URL", não "reescrever o código".

RISCO/CUIDADO:
    * `DATABASE_URL` NUNCA vai hardcoded — vem de variável de ambiente.
    * Em produção a senha vem de um Secret (Aula 8), nunca do `.env` commitado.
----------------------------------------------------------------------------
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# ---------------------------------------------------------------------------
# String de conexão.
#
# Formato: postgresql+psycopg2://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
#
# O host "db" é o NOME DO SERVIÇO no docker-compose.yml — dentro da rede do
# Compose, "db" resolve para o container do PostgreSQL. Fora do Compose,
# troque por "localhost".
#
# A partir da Aula 4, a URL vem de app/core/config.py (pydantic-settings),
# que lê a variável de ambiente DATABASE_URL (e usa um default em dev).
# ---------------------------------------------------------------------------
DATABASE_URL: str = settings.database_url

# `pool_pre_ping=True`: antes de usar uma conexão do pool, o SQLAlchemy faz um
# "ping" para garantir que ela não morreu (comum quando o banco reinicia).
# POR QUÊ: evita o erro "server closed the connection unexpectedly" depois de
# o container do banco ter ficado ocioso. RISCO de não usar: requisições
# falhando aleatoriamente após períodos sem uso.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

# `autoflush=False` e `autocommit` implícito desligado: o controle de quando
# salvar (commit) é nosso, explicitamente, nas rotas. Mais previsível para
# quem está aprendendo.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """Classe-base de todos os modelos ORM.

    Todo modelo (tabela) herda desta classe. O SQLAlchemy usa ela para saber
    quais tabelas existem (via ``Base.metadata``).
    """


def get_db() -> Generator[Session, None, None]:
    """Entrega uma sessão de banco para uma requisição e fecha ao final.

    Usado como dependência do FastAPI::

        @router.get("/tasks")
        def listar(db: Session = Depends(get_db)):
            ...

    O padrão ``try / finally`` garante que a sessão **sempre** é fechada,
    mesmo se a rota lançar exceção.

    POR QUÊ: uma sessão aberta e não fechada "vaza" conexões do pool; com o
    tempo o banco recusa novas conexões. O ``finally`` previne esse vazamento.

    Yields:
        Session: sessão SQLAlchemy válida durante a requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
