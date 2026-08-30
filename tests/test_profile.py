import re

import pytest


@pytest.fixture
def auth_client(client):
    """A test client with a logged-in session."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"
    return client


def test_profile_anonymous_redirects_to_login(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_profile_logged_in_returns_200(auth_client):
    assert auth_client.get("/profile").status_code == 200


def test_profile_shows_user_identity(auth_client):
    resp = auth_client.get("/profile")
    assert b"Demo User" in resp.data
    assert b"demo@spendly.com" in resp.data
    assert b"Member since" in resp.data


def test_profile_shows_three_summary_stats(auth_client):
    resp = auth_client.get("/profile")
    assert b"Total spent" in resp.data
    assert b"Transactions" in resp.data
    assert b"Top category" in resp.data
    assert b"42" in resp.data
    assert b"Food" in resp.data


def test_profile_transaction_table_has_three_plus_rows(auth_client):
    resp = auth_client.get("/profile")
    assert b"<table" in resp.data
    assert resp.data.count(b'class="cat-badge') >= 3
    assert b"Electricity bill" in resp.data
    assert b"Movie night" in resp.data


def test_profile_category_breakdown_has_three_plus(auth_client):
    resp = auth_client.get("/profile")
    assert resp.data.count(b'class="cat-row"') >= 3
    assert b"cat-bar" in resp.data
    assert b"Shopping" in resp.data
    assert b"Bills" in resp.data


def test_profile_navbar_logged_in_state(auth_client):
    resp = auth_client.get("/profile")
    assert b"Sign out" in resp.data
    assert b"Demo User" in resp.data


def test_profile_no_hex_colours(auth_client):
    resp = auth_client.get("/profile")
    assert re.search(rb"#[0-9a-fA-F]{3,8}\b", resp.data) is None


def test_profile_no_inline_styles(auth_client):
    resp = auth_client.get("/profile")
    assert b'style="' not in resp.data


def test_profile_extends_base(auth_client):
    resp = auth_client.get("/profile")
    assert b"nav-brand" in resp.data
    assert b"footer-name" in resp.data


def test_profile_links_profile_css(auth_client):
    resp = auth_client.get("/profile")
    assert b"css/profile.css" in resp.data


def test_logged_in_user_redirected_from_login(auth_client):
    resp = auth_client.get("/login")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_logged_in_user_redirected_from_register(auth_client):
    resp = auth_client.get("/register")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_anonymous_user_still_sees_login_page(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data
