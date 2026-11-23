import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_admin, get_tenant_db
from app.models import Admin
from app.schemas import AdminOut

# Semua endpoint di sini bergantung pada get_current_admin, jadi anonim ditolak.
router = APIRouter(
    prefix="/admins", tags=["admins"], dependencies=[Depends(get_current_admin)]
)


@router.get("", response_model=list[AdminOut])
def list_admins(session: Annotated[Session, Depends(get_tenant_db)]) -> list[Admin]:
    """Admin di Business milik pemanggil. Tidak ada filter business_id di query:
    pembatasannya murni dari RLS, jadi bila RLS bocor, test isolasi akan merah."""
    return list(session.scalars(select(Admin).order_by(Admin.created_at)))


@router.get("/{admin_id}", response_model=AdminOut)
def get_admin(
    admin_id: uuid.UUID, session: Annotated[Session, Depends(get_tenant_db)]
) -> Admin:
    admin = session.get(Admin, admin_id)
    if admin is None:
        # Admin Business lain tampil identik dengan Admin yang tidak ada.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin tidak ditemukan")
    return admin
