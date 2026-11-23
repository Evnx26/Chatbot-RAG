"""Isolasi antar Business di level database (ADR 0001).

Semua assertion memakai `app_user`. Test canary membuktikan bahwa harness
memang bisa membedakan role yang bypass RLS dari yang tidak.
"""

from sqlalchemy import text


def _count(conn, table: str) -> int:
    return conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


def _set_tenant(conn, business_id) -> None:
    conn.execute(
        text("SELECT set_config('app.current_business_id', :b, true)"), {"b": str(business_id)}
    )


# --- canary: test ini harus gagal kalau harness memakai role yang salah ---


def test_app_user_is_not_privileged(app_engine):
    with app_engine.connect() as conn:
        rolsuper, rolbypassrls = conn.execute(
            text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
        ).one()
    assert conn.engine.url.username == "app_user"
    assert not rolsuper
    assert not rolbypassrls


def test_canary_owner_sees_both_businesses(owner_engine, two_businesses):
    """Owner melewati RLS. Kalau ini 1, seed fixture-nya yang rusak."""
    with owner_engine.connect() as conn:
        assert _count(conn, "business") == 2
        assert _count(conn, "admin") == 2


# --- isolasi ---


def test_tenant_a_sees_only_its_own_rows(app_engine, two_businesses):
    a = two_businesses["a"]
    with app_engine.begin() as conn:
        _set_tenant(conn, a["business_id"])
        assert _count(conn, "business") == 1
        assert _count(conn, "admin") == 1
        assert conn.execute(text("SELECT id FROM admin")).scalar_one() == a["admin_id"]


def test_tenant_a_cannot_read_b_by_direct_id(app_engine, two_businesses):
    a, b = two_businesses["a"], two_businesses["b"]
    with app_engine.begin() as conn:
        _set_tenant(conn, a["business_id"])
        rows = conn.execute(
            text("SELECT * FROM admin WHERE id = :i OR business_id = :b"),
            {"i": b["admin_id"], "b": b["business_id"]},
        ).all()
    assert rows == []


def test_no_tenant_context_sees_nothing(app_engine, two_businesses):
    with app_engine.begin() as conn:
        assert _count(conn, "business") == 0
        assert _count(conn, "admin") == 0


def test_tenant_a_cannot_insert_admin_into_b(app_engine, two_businesses):
    import sqlalchemy.exc

    a, b = two_businesses["a"], two_businesses["b"]
    try:
        with app_engine.begin() as conn:
            _set_tenant(conn, a["business_id"])
            conn.execute(
                text(
                    "INSERT INTO admin (business_id, email, password_hash, full_name) "
                    "VALUES (:b, 'evil@example.com', 'x', 'Evil')"
                ),
                {"b": b["business_id"]},
            )
    except sqlalchemy.exc.DBAPIError:
        return
    raise AssertionError("insert lintas Business seharusnya ditolak policy WITH CHECK")


def test_tenant_a_cannot_update_or_delete_b(app_engine, owner_engine, two_businesses):
    a, b = two_businesses["a"], two_businesses["b"]
    with app_engine.begin() as conn:
        _set_tenant(conn, a["business_id"])
        updated = conn.execute(
            text("UPDATE admin SET full_name = 'hacked' WHERE id = :i"), {"i": b["admin_id"]}
        ).rowcount
    assert updated == 0
    with owner_engine.connect() as conn:
        name = conn.execute(
            text("SELECT full_name FROM admin WHERE id = :i"), {"i": b["admin_id"]}
        ).scalar_one()
    assert name == "Admin B"


def test_tenant_context_does_not_leak_across_transactions(app_engine, two_businesses):
    """set_config(..., true) berlaku per transaksi: koneksi pool tidak membawa konteks."""
    a = two_businesses["a"]
    with app_engine.begin() as conn:
        _set_tenant(conn, a["business_id"])
        assert _count(conn, "admin") == 1
    with app_engine.begin() as conn:
        assert _count(conn, "admin") == 0


def test_super_admin_table_is_unreachable_for_app_user(app_engine):
    import sqlalchemy.exc

    try:
        with app_engine.begin() as conn:
            conn.execute(text("SELECT * FROM super_admin"))
    except sqlalchemy.exc.DBAPIError:
        return
    raise AssertionError("app_user tidak boleh punya akses ke super_admin (ADR 0003)")


def test_every_table_with_business_id_has_forced_rls(owner_engine):
    """Penjaga tabel masa depan: tabel baru milik Business tanpa RLS = test merah."""
    with owner_engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relkind = 'r'
                  AND (c.relname = 'business' OR EXISTS (
                        SELECT 1 FROM pg_attribute a
                        WHERE a.attrelid = c.oid AND a.attname = 'business_id' AND NOT a.attisdropped))
                """
            )
        ).all()
    assert {r.relname for r in rows} >= {"business", "admin"}
    for name, enabled, forced in rows:
        assert enabled and forced, f"RLS belum aktif dan di-FORCE pada tabel {name}"
