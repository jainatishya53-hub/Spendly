from database.db import verify_credentials

GENERIC_ERROR = b"Incorrect email or password."


def test_get_login_unchanged(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data
    assert b"auth-error" not in resp.data


def test_successful_login(client, seeded_user):
    resp = client.post(
        "/login",
        data={"email": seeded_user["email"], "password": seeded_user["password"]},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")

    with client.session_transaction() as sess:
        assert sess["user_id"] is not None
        assert sess["user_name"] == "Demo User"


def test_login_email_case_insensitive(client, seeded_user):
    resp = client.post(
        "/login",
        data={"email": "Demo@Spendly.com", "password": seeded_user["password"]},
    )
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess["user_name"] == "Demo User"


def test_wrong_password(client, seeded_user):
    resp = client.post(
        "/login",
        data={"email": seeded_user["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 200
    assert GENERIC_ERROR in resp.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_unknown_email(client):
    resp = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "whatever12"},
    )
    assert resp.status_code == 200
    assert GENERIC_ERROR in resp.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_error_message_identical(client, seeded_user):
    wrong_pw = client.post(
        "/login",
        data={"email": seeded_user["email"], "password": "wrongpassword"},
    )
    unknown = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "wrongpassword"},
    )
    assert GENERIC_ERROR in wrong_pw.data
    assert GENERIC_ERROR in unknown.data


def test_blank_fields(client):
    resp = client.post("/login", data={"email": "", "password": ""})
    assert resp.status_code == 200
    assert GENERIC_ERROR in resp.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_error_repopulates_email(client, seeded_user):
    resp = client.post(
        "/login",
        data={"email": seeded_user["email"], "password": "wrongpassword"},
    )
    assert b'value="demo@spendly.com"' in resp.data
    assert b'value="wrongpassword"' not in resp.data
    assert b"demo123" not in resp.data


def test_login_form_uses_url_for(client):
    resp = client.get("/login")
    assert b'action="/login"' in resp.data


def test_logout_clears_session(client, seeded_user):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_when_logged_out(client):
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


def test_navbar_signed_out(client):
    resp = client.get("/")
    assert b"Sign in" in resp.data
    assert b"Sign out" not in resp.data


def test_navbar_signed_in(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    resp = client.get("/")
    assert b"Sign out" in resp.data
    assert b"Demo User" in resp.data


def test_verify_credentials_unit(db_path, seeded_user):
    row = verify_credentials("demo@spendly.com", "demo123")
    assert row is not None
    assert row["name"] == "Demo User"

    assert verify_credentials("demo@spendly.com", "wrongpassword") is None
    assert verify_credentials("nobody@example.com", "demo123") is None
