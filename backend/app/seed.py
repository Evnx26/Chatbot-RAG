"""Seed idempotent: Super Admin dan Business "Toko Demo" beserta Admin-nya.

Dijalankan sebagai migrator/owner (bypass RLS), karena membuat data lintas
Business adalah tugas operator, bukan tugas aplikasi.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config import get_settings, require
from app.models import Admin, Business, SuperAdmin
from app.security import hash_password

DEMO_BUSINESS_SLUG = "toko-demo"


def seed() -> None:
    settings = get_settings()
    engine = create_engine(require(settings.migrator_database_url, "MIGRATOR_DATABASE_URL"))
    with Session(engine) as session, session.begin():
        super_email = require(settings.seed_super_admin_email, "SEED_SUPER_ADMIN_EMAIL").lower()
        if session.scalar(text("SELECT 1 FROM super_admin WHERE email = :e"), {"e": super_email}) is None:
            session.add(
                SuperAdmin(
                    email=super_email,
                    password_hash=hash_password(
                        require(settings.seed_super_admin_password, "SEED_SUPER_ADMIN_PASSWORD")
                    ),
                )
            )

        business_id = session.scalar(
            text("SELECT id FROM business WHERE slug = :s"), {"s": DEMO_BUSINESS_SLUG}
        )
        if business_id is None:
            business = Business(name="Toko Demo", slug=DEMO_BUSINESS_SLUG)
            session.add(business)
            session.flush()
            business_id = business.id

        demo_email = require(settings.seed_demo_admin_email, "SEED_DEMO_ADMIN_EMAIL").lower()
        if session.scalar(text("SELECT 1 FROM admin WHERE lower(email) = :e"), {"e": demo_email}) is None:
            session.add(
                Admin(
                    business_id=business_id,
                    email=demo_email,
                    password_hash=hash_password(
                        require(settings.seed_demo_admin_password, "SEED_DEMO_ADMIN_PASSWORD")
                    ),
                    full_name="Admin Toko Demo",
                )
            )
    print("Seed selesai: Super Admin dan Toko Demo siap.")


if __name__ == "__main__":
    seed()
