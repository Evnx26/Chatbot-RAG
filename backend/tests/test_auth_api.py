import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.config import get_settings
from app.main import app

PASSWORD = "password-uji-123"


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def signup(client, name: str, email: str, password: str = PASSWORD):
    return client.post(
        "/auth/signup",
        json={"business_name": name, "full_name": f"Admin {name}", "email": email, "password": password},
    )


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_signup_creates_business_and_admin(client, owner_engine):
    res = signup(client, "Toko Baju Siti", "siti@example.com")
    assert res.status_code == 201
    me = client.get("/auth/me", headers=auth(res.json()["access_token"]))
    assert me.status_code == 200
    body = me.json()
    assert body["admin"]["email"] == "siti@example.com"
    assert body["business"]["name"] == "Toko Baju Siti"
    assert body["business"]["slug"].startswith("toko-baju-siti-")
    with owner_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM business")).scalar_one() == 1


def test_signup_rejects_duplicate_email_case_insensitive(client):
    assert signup(client, "Toko Satu", "dup@example.com").status_code == 201
    assert signup(client, "Toko Dua", "DUP@example.com").status_code == 409


def test_signup_validates_input(client):
    assert signup(client, "Toko", "bukan-email").status_code == 422
    assert signup(client, "Toko", "ok@example.com", password="pendek").status_code == 422


def test_password_is_stored_hashed(client, owner_engine):
    signup(client, "Toko", "hash@example.com")
    with owner_engine.connect() as conn:
        stored = conn.execute(text("SELECT password_hash FROM admin")).scalar_one()
    assert PASSWORD not in stored and stored.startswith("$argon2")


def test_login_success_and_failures(client):
    signup(client, "Toko", "login@example.com")
    ok = client.post("/auth/login", json={"email": "LOGIN@example.com", "password": PASSWORD})
    assert ok.status_code == 200
    assert client.get("/auth/me", headers=auth(ok.json()["access_token"])).status_code == 200
    wrong = client.post("/auth/login", json={"email": "login@example.com", "password": "salah-banget"})
    unknown = client.post("/auth/login", json={"email": "nobody@example.com", "password": PASSWORD})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_me_requires_valid_token(client):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers=auth("bukan.token.valid")).status_code == 401
    forged = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000000", "bid": "00000000-0000-0000-0000-000000000000",
         "role": "admin", "exp": 4102444800},
        "secret-salah-secret-salah-secret-salah",
        "HS256",
    )
    assert client.get("/auth/me", headers=auth(forged)).status_code == 401


def test_token_for_deleted_admin_is_rejected(client, owner_engine):
    token = signup(client, "Toko", "gone@example.com").json()["access_token"]
    with owner_engine.begin() as conn:
        conn.execute(text("DELETE FROM admin"))
    assert client.get("/auth/me", headers=auth(token)).status_code == 401


def test_super_admin_role_token_is_rejected_on_admin_endpoints(client):
    token = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000000", "bid": "00000000-0000-0000-0000-000000000000",
         "role": "super_admin", "exp": 4102444800},
        get_settings().jwt_secret,
        "HS256",
    )
    assert client.get("/auth/me", headers=auth(token)).status_code == 401


# --- isolasi lewat API ---


def test_admin_a_cannot_reach_business_b_via_api(client):
    token_a = signup(client, "Toko A", "a@example.com").json()["access_token"]
    token_b = signup(client, "Toko B", "b@example.com").json()["access_token"]
    admin_b_id = client.get("/auth/me", headers=auth(token_b)).json()["admin"]["id"]
    admin_a_id = client.get("/auth/me", headers=auth(token_a)).json()["admin"]["id"]

    listing = client.get("/admins", headers=auth(token_a))
    assert [a["id"] for a in listing.json()] == [admin_a_id]

    assert client.get(f"/admins/{admin_b_id}", headers=auth(token_a)).status_code == 404
    assert client.get(f"/admins/{admin_a_id}", headers=auth(token_a)).status_code == 200
    # Sebaliknya juga berlaku.
    assert client.get(f"/admins/{admin_a_id}", headers=auth(token_b)).status_code == 404


def test_admin_endpoints_require_auth(client):
    assert client.get("/admins").status_code == 401
    assert client.get("/admins/00000000-0000-0000-0000-000000000000").status_code == 401
