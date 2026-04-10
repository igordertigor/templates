{% if cookiecutter.add_strawberry == "y" %}
import strawberry
from strawberry.types import Info

from app.auth.oidc import get_current_user
from app.crud.users import users as users_crud
from app.graphql.types import UserType


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType | None:
        # Access the request via info.context to validate the token
        request = info.context["request"]
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=auth_header.removeprefix("Bearer ")
        )
        claims = await get_current_user(credentials)

        session = info.context["session"]
        user = users_crud.get_by_sub(session, claims.sub)
        if not user:
            return None
        return UserType(id=user.id, email=user.email, created_at=user.created_at)
{% endif %}
