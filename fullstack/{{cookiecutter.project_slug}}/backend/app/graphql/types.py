{% if cookiecutter.add_strawberry == "y" %}
"""
Strawberry output types.

These are separate from the SQLModel table definitions in tables.py.
The separation keeps the transport layer (GraphQL) decoupled from the
persistence layer. Map between them in your resolvers.
"""

from datetime import datetime

import strawberry


@strawberry.type
class UserType:
    id: int
    email: str
    created_at: datetime
{% endif %}
