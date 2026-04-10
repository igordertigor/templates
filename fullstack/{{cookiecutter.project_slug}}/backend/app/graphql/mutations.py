{% if cookiecutter.add_strawberry == "y" %}
import strawberry

from app.graphql.types import UserType


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def placeholder(self) -> bool:
        """Replace with real mutations."""
        return True
{% endif %}
