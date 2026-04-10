from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.tables import User


class CRUDUser(CRUDBase[User]):
    def get_by_email(self, session: Session, email: str) -> User | None:
        return session.exec(select(User).where(User.email == email)).first()

    def get_by_sub(self, session: Session, sub: str) -> User | None:
        """Look up a user by their Zitadel subject claim."""
        return session.exec(select(User).where(User.sub == sub)).first()

    def get_or_create(self, session: Session, *, sub: str, email: str) -> User:
        user = self.get_by_sub(session, sub)
        if not user:
            user = self.create(session, obj=User(sub=sub, email=email))
        return user


users = CRUDUser(User)
