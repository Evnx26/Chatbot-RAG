import re
import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import db
from app.deps import get_current_admin, get_tenant_db
from app.models import Admin, Business
from app.schemas import LoginRequest, MeResponse, SignupRequest, TokenResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

AnonSession = Annotated[Session, Depends(db.anonymous_session)]


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "business"
    return f"{base[:40]}-{secrets.token_hex(3)}"


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, session: AnonSession) -> TokenResponse:
    """Membuat Business baru beserta Admin pertamanya dalam satu transaksi."""
    business_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    try:
        # Konteks dipasang dulu ke Business yang akan dibuat, supaya policy
        # WITH CHECK meloloskan insert Business dan Admin-nya.
        db.set_tenant(session, business_id)
        session.add(Business(id=business_id, name=body.business_name, slug=_slugify(body.business_name)))
        session.flush()
        session.add(
            Admin(
                id=admin_id,
                business_id=business_id,
                email=body.email.lower(),
                password_hash=hash_password(body.password),
                full_name=body.full_name,
            )
        )
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email sudah terdaftar") from None
    return TokenResponse(access_token=create_access_token(admin_id, business_id))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: AnonSession) -> TokenResponse:
    row = session.execute(
        text("SELECT * FROM auth_find_admin_by_email(:email)"), {"email": body.email}
    ).first()
    # Selalu verifikasi hash (palsu bila email tak ada) agar waktu respons sama.
    if not verify_password(body.password, row.password_hash if row else None) or row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email atau password salah")
    return TokenResponse(access_token=create_access_token(row.id, row.business_id))


@router.get("/me", response_model=MeResponse)
def me(
    admin: Annotated[Admin, Depends(get_current_admin)],
    session: Annotated[Session, Depends(get_tenant_db)],
) -> MeResponse:
    business = session.get(Business, admin.business_id)
    return MeResponse(admin=admin, business=business)
