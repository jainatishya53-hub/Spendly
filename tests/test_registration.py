import sqlite3

import pytest
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email


def count_users():
    conn = get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def test_get_register_unchanged(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create your account" in resp.data
    assert b"auth-error" not in resp.data


def test_successful_signup(client):
    resp = client.post(
        "/register",
        data={"name": "Alice Smith", "email": "alice@example.com", "password": "supersecret"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert count_users() == 1

    row = get_user_by_email("alice@example.com")
    assert row is not None
    assert row["name"] == "Alice Smith"
    assert row["email"] == "alice@example.com"
    assert row["password_hash"] != "supersecret"
    assert check_password_hash(row["password_hash"], "supersecret")


def test_duplicate_email(client, seeded_user):
    before = count_users()
    resp = client.post(
        "/register",
        data={"name": "Impostor", "email": "demo@spendly.com", "password": "whatever12"},
    )
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert count_users() == before


def test_duplicate_email_case_insensitive(client, seeded_user):
    before = count_users()
    resp = client.post(
        "/register",
        data={"name": "Impostor", "email": "Demo@Spendly.com", "password": "whatever12"},
    )
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert count_users() == before


def test_blank_name(client):
    resp = client.post(
        "/register",
        data={"name": "   ", "email": "bob@example.com", "password": "longenough"},
    )
    assert resp.status_code == 200
    assert b"enter your name" in resp.data
    assert count_users() == 0


def test_malformed_email(client):
    resp = client.post(
        "/register",
        data={"name": "Bob", "email": "bobexample.com", "password": "longenough"},
    )
    assert resp.status_code == 200
    assert b"valid email" in resp.data
    assert count_users() == 0


def test_short_password(client):
    resp = client.post(
        "/register",
        data={"name": "Bob", "email": "bob@example.com", "password": "short"},
    )
    assert resp.status_code == 200
    assert b"8 characters" in resp.data
    assert count_users() == 0


def test_error_repopulates_fields(client):
    resp = client.post(
        "/register",
        data={"name": "Charlie Day", "email": "charlie@example.com", "password": "short"},
    )
    assert resp.status_code == 200
    assert b'value="Charlie Day"' in resp.data
    assert b'value="charlie@example.com"' in resp.data


def test_password_boundary(client):
    ok = client.post(
        "/register",
        data={"name": "Eight", "email": "eight@example.com", "password": "abcdefgh"},
    )
    assert ok.status_code == 302
    assert count_users() == 1

    too_short = client.post(
        "/register",
        data={"name": "Seven", "email": "seven@example.com", "password": "abcdefg"},
    )
    assert too_short.status_code == 200
    assert count_users() == 1


def test_email_stored_lowercased(client):
    resp = client.post(
        "/register",
        data={"name": "Mixed", "email": "MixedCase@Example.com", "password": "longenough"},
    )
    assert resp.status_code == 302
    assert get_user_by_email("mixedcase@example.com") is not None


def test_create_user_raises_on_duplicate(db_path):
    create_user("First", "dup@example.com", "longenough")
    with pytest.raises(sqlite3.IntegrityError):
        create_user("Second", "dup@example.com", "longenough")
