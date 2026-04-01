import httpx
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

security = HTTPBearer()

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    async with httpx.AsyncClient(trust_env=False) as client:
        resp = await client.get(f"{settings.FRONTEND_URL}/api/auth/jwks")
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


def _get_public_key(jwks: dict, kid: str):
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return jwt.algorithms.OKPAlgorithm.from_jwk(key)
    raise HTTPException(status_code=401, detail="Unauthorized")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    try:
        header = jwt.get_unverified_header(credentials.credentials)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Unauthorized")

        jwks = await _get_jwks()
        public_key = _get_public_key(jwks, kid)

        payload = jwt.decode(
            credentials.credentials,
            public_key,
            algorithms=["EdDSA"],
            options={"verify_aud": False},
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Unauthorized")
