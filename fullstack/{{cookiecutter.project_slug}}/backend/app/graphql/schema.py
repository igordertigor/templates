{% if cookiecutter.add_strawberry == "y" %}
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.queries import Query
from app.graphql.mutations import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
{% endif %}
