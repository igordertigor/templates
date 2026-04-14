"""
Authentik OIDC / JWT validation.

FastAPI dependency `get_current_user` validates the Bearer token on every
request and returns the decoded claims. Use it in routers like:

    @router.get("/me")
    async def me(claims: Claims = Depends(get_current_user)):
        return claims
"""

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.settings import settings

bearer_scheme = HTTPBearer()

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.authentik_issuer}/application/o/{settings.authentik_app_slug}/.well-known/openid-configuration"
            )
            resp.raise_for_status()
            oidc_config = resp.json()
            jwks_resp = await client.get(oidc_config["jwks_uri"])
            jwks_resp.raise_for_status()
            _jwks_cache = jwks_resp.json()
    return _jwks_cache


class Claims(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Claims:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwks = await _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.authentik_client_id or None,
            options={"verify_aud": bool(settings.authentik_client_id)},
        )
        return Claims(
            sub=payload["sub"],
            email=payload.get("email"),
            name=payload.get("name"),
        )
    except JWTError:
        raise credentials_exception

{% if cookiecutter.auth_client_credentials == "y" %}

async def require_service_account(
    claims: Claims = Depends(get_current_user),
) -> Claims:
    """
    Dependency for endpoints that should only be called by service accounts
    (client credentials flow). Adjust the check to match your Authentik roles
    or client ID conventions.
    """
    # Example: check for a custom claim set in Authentik policies/expressions
    # if "service_account" not in claims.roles:
    #     raise HTTPException(status_code=403, detail="Service accounts only")
    return claims
{% endif %}
