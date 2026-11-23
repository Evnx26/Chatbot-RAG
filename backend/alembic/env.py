from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings, require
from app.models import Base

config = context.config
target_metadata = Base.metadata


def _url() -> str:
    # Test bisa menimpa lewat config.set_main_option("sqlalchemy.url", ...).
    return config.get_main_option("sqlalchemy.url") or require(
        get_settings().migrator_database_url, "MIGRATOR_DATABASE_URL"
    )


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
