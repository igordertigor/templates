from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.oidc import Claims, get_current_user
from app.crud.users import users as users_crud
from app.db import get_session
from app.tables import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_me(
    session: Session = Depends(get_session),
    claims: Claims = Depends(get_current_user),
) -> User:
    """Return the current user, creating them on first login."""
    return users_crud.get_or_create(
        session, sub=claims.sub, email=claims.email or ""
    )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: Claims = Depends(get_current_user),
) -> User:
    user = users_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
