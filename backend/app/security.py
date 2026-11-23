import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import get_settings, require

_hasher = PasswordHash.recommended()
# Hash palsu untuk menyamakan waktu respons saat email tidak ditemukan.
_DUMMY_HASH = _hasher.hash("dummy-password-for-timing")

ALGORITHM = "HS256"
ROLE_ADMIN = "admin"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    return _hasher.verify(password, password_hash or _DUMMY_HASH) and bool(password_hash)


def create_access_token(admin_id: uuid.UUID, business_id: uuid.UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(admin_id),
        "bid": str(business_id),
        "role": ROLE_ADMIN,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, require(settings.jwt_secret, "JWT_SECRET"), ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Melempar jwt.PyJWTError bila token tidak valid atau kedaluwarsa."""
    return jwt.decode(
        token,
        require(get_settings().jwt_secret, "JWT_SECRET"),
        algorithms=[ALGORITHM],
        options={"require": ["sub", "bid", "role", "exp"]},
    )
