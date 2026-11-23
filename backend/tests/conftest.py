"""Test jalan terhadap Postgres sungguhan di docker-compose (SQLite tidak punya RLS).

Setiap sesi test membuat database `chatbot_test` baru lewat role owner, menjalankan
migrasi Alembic, lalu seluruh assertion dijalankan sebagai `app_user`.
Fixture seed/cleanup memakai role owner. Assertion tidak boleh memakainya.
"""

import os
import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
TEST_DB = "chatbot_test"

_env = {**dotenv_values(ROOT / ".env"), **os.environ}
_host = f"localhost:{_env.get('DB_HOST_PORT', '5433')}"
_owner = f"{_env['POSTGRES_USER']}:{_env['POSTGRES_PASSWORD']}"

OWNER_URL = f"postgresql+psycopg://{_owner}@{_host}/{TEST_DB}"
OWNER_ADMIN_URL = f"postgresql+psycopg://{_owner}@{_host}/postgres"
APP_URL = f"postgresql+psycopg://app_user:{_env['APP_DB_PASSWORD']}@{_host}/{TEST_DB}"

# Harus diset sebelum `app` di-import oleh test mana pun.
os.environ["DATABASE_URL"] = APP_URL
os.environ["MIGRATOR_DATABASE_URL"] = OWNER_URL
os.environ["JWT_SECRET"] = "test-secret-" + "x" * 32


@pytest.fixture(scope="session", autouse=True)
def _database():
    admin_engine = create_engine(OWNER_ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB}"))
    admin_engine.dispose()

    cfg = Config(str(ROOT / "backend" / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "backend" / "alembic"))
    cfg.set_main_option("sqlalchemy.url", OWNER_URL)
    command.upgrade(cfg, "head")
    yield


@pytest.fixture(scope="session")
def owner_engine(_database):
    """Role owner/superuser: melewati RLS. HANYA untuk seed dan cleanup."""
    engine = create_engine(OWNER_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def app_engine(_database):
    """Role app_user: sama persis dengan yang dipakai FastAPI. Tunduk pada RLS."""
    engine = create_engine(APP_URL)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables(owner_engine):
    yield
    with owner_engine.begin() as conn:
        conn.execute(text("TRUNCATE business, admin, super_admin CASCADE"))


@pytest.fixture
def two_businesses(owner_engine):
    """Dua Business, masing-masing dengan satu Admin, dibuat lewat owner."""
    ids = {}
    with owner_engine.begin() as conn:
        for key in ("a", "b"):
            business_id = uuid.uuid4()
            admin_id = uuid.uuid4()
            conn.execute(
                text("INSERT INTO business (id, name, slug) VALUES (:id, :n, :s)"),
                {"id": business_id, "n": f"Business {key.upper()}", "s": f"business-{key}"},
            )
            conn.execute(
                text(
                    "INSERT INTO admin (id, business_id, email, password_hash, full_name) "
                    "VALUES (:id, :bid, :e, 'x', :n)"
                ),
                {"id": admin_id, "bid": business_id, "e": f"{key}@example.com", "n": f"Admin {key.upper()}"},
            )
            ids[key] = {"business_id": business_id, "admin_id": admin_id}
    return ids
