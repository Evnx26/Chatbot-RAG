import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import db
from app.models import Admin
from app.security import ROLE_ADMIN, decode_access_token

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    admin_id: uuid.UUID
    business_id: uuid.UUID


def _unauthorized() -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Sesi tidak valid",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> AuthContext:
    """business_id hanya berasal dari token yang ditandatangani server, tidak
    pernah dari body, query, atau path request."""
    if credentials is None:
        raise _unauthorized()
    try:
        claims = decode_access_token(credentials.credentials)
        if claims["role"] != ROLE_ADMIN:
            raise _unauthorized()
        return AuthContext(uuid.UUID(claims["sub"]), uuid.UUID(claims["bid"]))
    except (jwt.PyJWTError, ValueError):
        raise _unauthorized() from None


def get_tenant_db(
    auth: Annotated[AuthContext, Depends(get_auth_context)],
) -> Iterator[Session]:
    """Sesi DB dengan konteks Business dari token. Endpoint yang menulis data
    harus memanggil session.commit() sendiri."""
    yield from db.tenant_session(auth.business_id)


def get_current_admin(
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    session: Annotated[Session, Depends(get_tenant_db)],
) -> Admin:
    """Token valid belum cukup: Admin-nya harus benar-benar ada di Business
    pada token (dicek lewat RLS). Admin yang sudah dihapus otomatis ditolak."""
    admin = session.get(Admin, auth.admin_id)
    if admin is None:
        raise _unauthorized()
    return admin
