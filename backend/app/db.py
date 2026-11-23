import uuid
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings, require


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        require(get_settings().database_url, "DATABASE_URL"), pool_pre_ping=True
    )


def _new_session() -> Session:
    return sessionmaker(get_engine(), expire_on_commit=False)()


def set_tenant(session: Session, business_id: uuid.UUID) -> None:
    """Pasang konteks Business untuk transaksi ini.

    `true` membuat setting berlaku per transaksi saja, jadi koneksi yang
    dikembalikan ke pool tidak membawa konteks ke request berikutnya.
    Setelah commit, konteks hilang dan query berikutnya tidak melihat apa pun.
    """
    session.execute(
        text("SELECT set_config('app.current_business_id', :bid, true)"),
        {"bid": str(business_id)},
    )


def anonymous_session() -> Iterator[Session]:
    """Sesi tanpa konteks Business: RLS menyembunyikan semua data tenant.
    Untuk signup (konteks dipasang sendiri) dan login (lewat fungsi SECURITY DEFINER)."""
    with _new_session() as session:
        yield session


def tenant_session(business_id: uuid.UUID) -> Iterator[Session]:
    with _new_session() as session:
        set_tenant(session, business_id)
        yield session
