"""
All SQLModel table definitions live here.

Keeping all tables in a single file ensures Alembic can always detect them —
SQLModel only registers table metadata when the class is imported, and a single
import of this module is all that is needed in migrations/env.py.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    sub: str = Field(unique=True, index=True)  # Zitadel subject claim
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Add further table definitions below.
# Example:
#
# class Item(SQLModel, table=True):
#     __tablename__ = "items"
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     title: str
#     owner_id: int = Field(foreign_key="users.id")
