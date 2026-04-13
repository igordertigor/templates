from typing import Generic, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

TableType = TypeVar("TableType", bound=SQLModel)


class CRUDBase(Generic[TableType]):
    def __init__(self, model: type[TableType]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, id: int) -> TableType | None:
        return await session.get(self.model, id)

    async def get_multi(
        self, session: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> list[TableType]:
        return list(await session.exec(select(self.model).offset(offset).limit(limit)))

    async def create(self, session: AsyncSession, *, obj: TableType) -> TableType:
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(self, session: AsyncSession, *, db_obj: TableType, updates: dict) -> TableType:
        for field, value in updates.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, *, id: int) -> TableType | None:
        obj = await session.get(self.model, id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj
