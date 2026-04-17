# auth/sso.py

import logging
import httpx
import jwt
from jwt import PyJWKClient
from config_settings import get_settings

logger = logging.getLogger("sso.auth")

_jwks_client = None


def _get_jwks_client(tenant_id: str) -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


async def exchange_code_for_tokens(code: str) -> dict:
    settings = get_settings()
    token_url = (
        f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}"
        f"/oauth2/v2.0/token"
    )
    data = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "client_secret": settings.MICROSOFT_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": "openid profile email",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
        if resp.status_code != 200:
            logger.error("Token exchange failed: %s", resp.text)
            resp.raise_for_status()
        return resp.json()


def validate_id_token(id_token: str) -> dict:
    settings = get_settings()
    jwks_client = _get_jwks_client(settings.MICROSOFT_TENANT_ID)
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    claims = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.MICROSOFT_CLIENT_ID,
        issuer=f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/v2.0",
    )
    logger.info("Validated id_token for: %s", claims.get("preferred_username"))
    return claims