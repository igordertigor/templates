from typing import AsyncIterator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.settings import settings

engine: AsyncEngine = create_async_engine(settings.database_url)


def create_db_and_tables() -> None:
    """Only used in tests. Migrations handle production schema."""
    SQLModel.metadata.create_all(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
