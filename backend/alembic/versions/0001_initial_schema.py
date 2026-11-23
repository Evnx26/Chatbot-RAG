"""initial schema: business, admin, super_admin, RLS

Revision ID: 0001
Revises:
Create Date: 2026-11-23
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Tabel milik Business: kolom tenant-nya dan nama tabel.
# Setiap tabel baru milik Business WAJIB ditambahkan lewat enable_tenant_rls().
TENANT_ISOLATION_PREDICATE = "app_current_business_id()"


def enable_tenant_rls(table: str, column: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    # FORCE: pemilik tabel pun tunduk pada policy (superuser tetap bypass).
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY tenant_isolation ON {table}
          USING ({column} = {TENANT_ISOLATION_PREDICATE})
          WITH CHECK ({column} = {TENANT_ISOLATION_PREDICATE})
        """
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Konteks tenant per transaksi. Kalau belum di-set, hasilnya NULL, sehingga
    # policy tidak meloloskan satu baris pun (fail closed).
    op.execute(
        """
        CREATE FUNCTION app_current_business_id() RETURNS uuid
          LANGUAGE sql STABLE
          AS $$ SELECT NULLIF(current_setting('app.current_business_id', true), '')::uuid $$
        """
    )

    op.create_table(
        "business",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("slug", sa.Text, nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "admin",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("full_name", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_admin_business_id", "admin", ["business_id"])
    # Login hanya memakai email + password, jadi email unik secara global.
    op.execute("CREATE UNIQUE INDEX uq_admin_email_lower ON admin (lower(email))")

    op.create_table(
        "super_admin",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    enable_tenant_rls("business", "id")
    enable_tenant_rls("admin", "business_id")

    # Login perlu mencari Admin lewat email SEBELUM konteks tenant ada, padahal
    # RLS menyembunyikan semua baris. Jalur sempit ini dijalankan dengan hak
    # pemilik fungsi (bypass RLS) dan hanya mengembalikan satu Admin per email.
    op.execute(
        """
        CREATE FUNCTION auth_find_admin_by_email(p_email text)
          RETURNS TABLE (
            id uuid, business_id uuid, email text, password_hash text, full_name text
          )
          LANGUAGE sql STABLE SECURITY DEFINER
          SET search_path = public, pg_temp
          AS $$
            SELECT a.id, a.business_id, a.email, a.password_hash, a.full_name
            FROM admin a
            WHERE lower(a.email) = lower(p_email)
            LIMIT 1
          $$
        """
    )
    op.execute("REVOKE ALL ON FUNCTION auth_find_admin_by_email(text) FROM PUBLIC")
    op.execute("GRANT EXECUTE ON FUNCTION auth_find_admin_by_email(text) TO app_user")

    # Hak minimum untuk app_user. super_admin sengaja tidak diberi hak apa pun
    # (ADR 0003); hak itu baru ditambahkan di Fase 6 bila diperlukan.
    op.execute("GRANT SELECT, INSERT, UPDATE ON business, admin TO app_user")


def downgrade() -> None:
    op.execute("DROP FUNCTION auth_find_admin_by_email(text)")
    op.drop_table("super_admin")
    op.drop_table("admin")
    op.drop_table("business")
    op.execute("DROP FUNCTION app_current_business_id()")
