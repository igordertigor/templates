from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users

{% if cookiecutter.add_strawberry == "y" %}
from app.graphql.schema import schema
from strawberry.fastapi import GraphQLRouter
{% endif %}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="{{ cookiecutter.project_name }}",
        description="{{ cookiecutter.project_description }}",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # REST routers
    app.include_router(users.router, prefix="/api/v1")

    {% if cookiecutter.add_strawberry == "y" %}
    # GraphQL
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")
    {% endif %}

    return app


app = create_app()
