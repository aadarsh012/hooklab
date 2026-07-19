"""JWT verification for the FastAPI backend.

The Next.js BFF proxy attaches a short-lived Better Auth JWT as a Bearer token.
This module verifies that token *statelessly* against Better Auth's public keys
(the /api/auth/jwks endpoint) — no database call, no round-trip to Better Auth.

Better Auth's JWT plugin signs with EdDSA by default; we also accept the common
asymmetric algorithms in case the plugin is reconfigured. Only asymmetric
algorithms are allowed (never HMAC) to avoid algorithm-confusion attacks — the
signing key is always selected from the public JWKS by the token's `kid`.
"""

from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from pydantic import BaseModel

from config import config

# Asymmetric algorithms only. EdDSA is Better Auth's default.
_ALLOWED_ALGORITHMS = ["EdDSA", "ES256", "RS256"]

# Lazily-initialised JWKS client. PyJWKClient fetches the key set once and caches
# it, refetching only when a token carries an unrecognised `kid` (key rotation).
_jwks_client: Optional[PyJWKClient] = None

# Bearer scheme — surfaces the "Authorize" box in the OpenAPI docs.
_bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """The authenticated user, derived from verified JWT claims."""

    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None


def _get_jwks_client() -> PyJWKClient:
    """Return the shared JWKS client, creating it on first use."""
    global _jwks_client
    if _jwks_client is None:
        if not config.BETTER_AUTH_JWKS_URL:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth is not configured (BETTER_AUTH_JWKS_URL is unset).",
            )
        _jwks_client = PyJWKClient(config.BETTER_AUTH_JWKS_URL)
    return _jwks_client


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> CurrentUser:
    """FastAPI dependency: verify the Bearer JWT and return the current user.

    Raises 401 for any missing/invalid/expired token.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=_ALLOWED_ALGORITHMS,
            issuer=config.BETTER_AUTH_ISSUER if config.BETTER_AUTH_ISSUER else None,
            # Better Auth JWTs don't always carry an audience; issuer + signature
            # + expiry are the checks we rely on here.
            options={"verify_aud": False},
        )
    except HTTPException:
        raise
    except Exception as exc:  # invalid signature, expired, bad issuer, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = claims.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        user_id=subject,
        email=claims.get("email"),
        name=claims.get("name"),
    )
