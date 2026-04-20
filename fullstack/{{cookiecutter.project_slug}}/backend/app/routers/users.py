import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.oidc import Claims, get_current_user
from app.crud.users import users as users_crud
from app.db import get_session
from app.tables import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_me(
    session: AsyncSession = Depends(get_session),
    claims: Claims = Depends(get_current_user),
) -> User:
    """Return the current user, creating them on first login."""
    return await users_crud.get_or_create(
        session, sub=claims.sub, email=claims.email or ""
    )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: Claims = Depends(get_current_user),
) -> User:
    user = await users_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
