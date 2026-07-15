"""
Camada HTTP da aplicação — routers do FastAPI.

Cada arquivo ``routes_<dominio>.py`` exporta um :class:`fastapi.APIRouter`
agrupando endpoints relacionados, que é registrado em
:func:`app.main.app` via ``include_router``.

Convenções desta camada:
    * Sempre declarar ``response_model`` em rotas.
    * Sempre incluir ``summary``, ``description`` e exemplos para o Swagger.
    * Nunca colocar regra de negócio aqui — apenas orquestração HTTP.
      A lógica vive em ``app.services`` ou ``app.db`` (a partir da Aula 3).
"""
