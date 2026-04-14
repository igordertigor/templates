{% if cookiecutter.auth_device_flow == "y" %}
"""
OAuth2 Device Authorization Flow helper.

Use this in a CLI tool or any client without a browser. Example usage:

    from app.auth.device import DeviceFlowClient

    client = DeviceFlowClient()
    device_resp = await client.start()
    print(f"Visit {device_resp.verification_uri} and enter {device_resp.user_code}")
    token = await client.poll(device_resp.device_code, device_resp.interval)
    print(f"Access token: {token.access_token}")
"""

import asyncio

import httpx
from pydantic import BaseModel

from app.settings import settings


class DeviceAuthResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str | None = None
    expires_in: int
    interval: int = 5


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    id_token: str | None = None


class DeviceFlowClient:
    def __init__(self, client_id: str | None = None) -> None:
        self.client_id = client_id or settings.authentik_client_id
        self.base_url = settings.authentik_issuer

    async def start(self, scopes: list[str] | None = None) -> DeviceAuthResponse:
        scopes = scopes or ["openid", "email", "profile", "offline_access"]
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}device/",
                data={
                    "client_id": self.client_id,
                    "scope": " ".join(scopes),
                },
            )
            resp.raise_for_status()
            return DeviceAuthResponse(**resp.json())

    async def poll(
        self, device_code: str, interval: int = 5, timeout: int = 300
    ) -> TokenResponse:
        elapsed = 0
        async with httpx.AsyncClient() as client:
            while elapsed < timeout:
                await asyncio.sleep(interval)
                elapsed += interval
                resp = await client.post(
                    f"{self.base_url}token/",
                    data={
                        "client_id": self.client_id,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "device_code": device_code,
                    },
                )
                if resp.status_code == 200:
                    return TokenResponse(**resp.json())
                error = resp.json().get("error")
                if error == "authorization_pending":
                    continue
                elif error == "slow_down":
                    interval += 5
                else:
                    raise RuntimeError(f"Device flow error: {error}")
        raise TimeoutError("Device authorization timed out")
{% endif %}
