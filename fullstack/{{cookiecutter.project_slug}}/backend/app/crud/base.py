from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

TableType = TypeVar("TableType", bound=SQLModel)


class CRUDBase(Generic[TableType]):
    def __init__(self, model: type[TableType]) -> None:
        self.model = model

    def get(self, session: Session, id: int) -> TableType | None:
        return session.get(self.model, id)

    def get_multi(
        self, session: Session, *, offset: int = 0, limit: int = 100
    ) -> list[TableType]:
        return list(session.exec(select(self.model).offset(offset).limit(limit)))

    def create(self, session: Session, *, obj: TableType) -> TableType:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def update(self, session: Session, *, db_obj: TableType, updates: dict) -> TableType:
        for field, value in updates.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, *, id: int) -> TableType | None:
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
