import pytest
from werkzeug.security import generate_password_hash

import database.db as db_module
from database.db import get_db, init_db


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Point the app at a throwaway SQLite file and create the schema."""
    path = tmp_path / "test.db"
    monkeypatch.setattr(db_module, "DB_PATH", str(path))
    init_db()
    return path


@pytest.fixture(autouse=True)
def _never_touch_real_db(db_path):
    """Fail fast if any test somehow escapes the temp database."""
    assert db_module.DB_PATH == str(db_path)


@pytest.fixture
def client(db_path):
    import app as app_module

    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


@pytest.fixture
def seeded_user(db_path):
    """Insert a single known user for duplicate-email tests."""
    user = {"name": "Demo User", "email": "demo@spendly.com", "password": "demo123"}
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (user["name"], user["email"], generate_password_hash(user["password"])),
        )
        conn.commit()
    finally:
        conn.close()
    return user
