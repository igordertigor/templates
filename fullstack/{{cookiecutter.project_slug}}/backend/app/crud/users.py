from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.tables import User


class CRUDUser(CRUDBase[User]):
    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        return await session.exec(select(User).where(User.email == email)).first()

    async def get_by_sub(self, session: AsyncSession, sub: str) -> User | None:
        """Look up a user by their Authentik subject claim."""
        return await session.exec(select(User).where(User.sub == sub)).first()

    async def get_or_create(self, session: AsyncSession, *, sub: str, email: str) -> User:
        user = await self.get_by_sub(session, sub)
        if not user:
            user = await self.create(session, obj=User(sub=sub, email=email))
        return user


users = CRUDUser(User)
