from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Semua nilai datang dari environment (docker-compose menyuplainya).

    Setiap service hanya menerima variabel yang dia butuhkan, jadi semuanya
    opsional di sini dan baru divalidasi lewat `require()` saat dipakai.
    """

    model_config = SettingsConfigDict(extra="ignore")

    # URL koneksi sebagai app_user (tunduk pada RLS). Dipakai FastAPI.
    database_url: str | None = None
    # URL koneksi sebagai migrator/owner. Dipakai Alembic dan seed saja.
    migrator_database_url: str | None = None

    jwt_secret: str | None = None
    jwt_expire_minutes: int = 60

    seed_super_admin_email: str | None = None
    seed_super_admin_password: str | None = None
    seed_demo_admin_email: str | None = None
    seed_demo_admin_password: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def require(value: str | None, name: str) -> str:
    if not value:
        raise RuntimeError(f"Environment variable {name} is required but not set")
    return value
