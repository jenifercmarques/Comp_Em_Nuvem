"""
Camada de persistência (banco de dados) do CloudTask AI SaaS.

Reúne:
    * :mod:`app.db.database` — conexão (engine) e sessões SQLAlchemy.
    * :mod:`app.db.models`   — tabelas (modelos ORM).
    * :mod:`app.db.schemas`  — schemas Pydantic de entrada/saída da API.

POR QUÊ separar em três arquivos: cada um tem uma responsabilidade clara
(conexão, formato no banco, formato na API). Isso facilita o aluno enxergar
a diferença entre "como o dado é guardado" (model) e "como o dado entra/sai
pela API" (schema).
"""
