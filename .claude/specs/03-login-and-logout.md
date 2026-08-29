# Spec: Login and Logout

## Overview
This step completes authentication by making the existing login page work and by
turning the `/logout` stub into a real route. Today `GET /login` only renders
`login.html`, the form POSTs to a hardcoded `/login` that no handler accepts, and
`/logout` returns the raw string `"Logout — coming in Step 3"`. This feature adds
`POST /login` handling — look up the account by email, verify the submitted
password against the stored werkzeug hash, and on success store the user's id and
name in a Flask `session` and redirect to the landing page; on failure re-render
`login.html` with a generic error. `GET /logout` clears the session and redirects
to the landing page. The shared navbar in `base.html` becomes session-aware so a
signed-in user sees their name and a "Sign out" link instead of "Sign in / Get
started". It sits on top of Step 2 (registration), which creates the accounts this
step signs in, and it is the last piece of auth before the profile and expense
steps that will depend on `session["user_id"]`.

## Depends on
- **Step 1 — Database setup** — `users` table, `get_db()`, `init_db()`,
  `seed_db()` (all exist and work).
- **Step 2 — Registration** — `create_user()` / `get_user_by_email()` in
  `database/db.py` and the working `POST /register` flow that produces accounts
  with a hashed `password_hash` (all exist and work).

## Routes
- `GET /login` — render the login form — public *(already implemented; will be
  merged into a single `methods=["GET", "POST"]` handler)*
- `POST /login` — validate input, verify credentials, set `session["user_id"]`
  and `session["user_name"]`, redirect to `/` on success; re-render `login.html`
  with a generic `error` on failure — public
- `GET /logout` — clear the session and redirect to `/` — public *(currently a
  raw-string stub; this step implements it)*

## Database changes
No database changes. The existing `users` schema from Step 1 already has
everything needed (`email` UNIQUE NOT NULL, `password_hash` NOT NULL). Credential
lookup reuses the existing `get_user_by_email()` helper; a new
`verify_credentials()` helper in `database/db.py` wraps it plus the werkzeug hash
check. No inline SQL in routes.

## Templates
- **Create:** none.
- **Modify:**
  - `templates/login.html`
    - Change `<form method="POST" action="/login">` to
      `action="{{ url_for('login') }}"` — no hardcoded URLs.
    - Keep the existing `{% if error %}<div class="auth-error">` block — it is
      already styled in `style.css`.
    - Repopulate the email input on error with `value="{{ email or '' }}"` so the
      user does not retype it. Never repopulate the password field.
  - `templates/base.html`
    - Make `.nav-links` session-aware: when `session.user_id` is set, show the
      user's name (`{{ session.user_name }}`) and a "Sign out" link to
      `{{ url_for('logout') }}`; otherwise show the current "Sign in" /
      "Get started" links unchanged.
    - Use `url_for()` for the logout link — no hardcoded path.

## Files to change
- `app.py`
  - Add `session` to the `flask` import (`redirect`, `render_template`,
    `request`, `url_for` are already imported).
  - Set `app.secret_key` (read from `os.environ.get("SECRET_KEY", <dev default>)`)
    so `session` works — required for this step; `import os` at top.
  - Replace the `GET`-only `login()` route with a `methods=["GET", "POST"]`
    handler: strip/lowercase email, require email + password, call the new
    `verify_credentials()` helper, set `session["user_id"]` /
    `session["user_name"]` and `redirect(url_for("landing"))` on success, or
    re-render `login.html` with a single generic `error` and the submitted
    `email` on failure.
  - Implement `logout()`: `session.clear()` then `redirect(url_for("landing"))`.
    Remove the raw-string return.
- `database/db.py`
  - Add `verify_credentials(email, password)` — calls `get_user_by_email()`,
    runs `werkzeug.security.check_password_hash` against `password_hash`, returns
    the user `Row` on match or `None` otherwise. Add `check_password_hash` to the
    existing `werkzeug.security` import.
- `templates/login.html` — see Templates section.
- `templates/base.html` — see Templates section.

## Files to create
- `.claude/specs/03-login-and-logout.md` — this spec.
- `tests/test_login.py` — pytest coverage for the flow (see Definition of done).

## New dependencies
No new dependencies. `flask.session` is part of Flask core;
`werkzeug.security.check_password_hash` ships with the already-pinned `werkzeug`.
`pytest` / `pytest-flask` are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only (`?` placeholders) — never f-strings or `.format()`
  in SQL. (Reuses `get_user_by_email()`, which already complies.)
- Passwords hashed with werkzeug — verify with
  `werkzeug.security.check_password_hash`; never compare raw passwords, never log
  the password, never store or echo it back to the template.
- All DB access lives in `database/db.py` — the route calls
  `verify_credentials()`; it does not open connections or write SQL.
- Use CSS variables — never hardcode hex values. `.auth-error` already exists; no
  new CSS is expected. Any nav tweak reuses existing classes / variables.
- All templates extend `base.html` (`login.html` already does).
- Use `url_for()` for every internal link and the form `action` — no hardcoded
  paths anywhere touched by this step.
- Route function keeps one responsibility per path: GET renders, POST processes,
  logout clears + redirects.
- Validation / auth rules:
  - `email` — required, stripped, lowercased before lookup.
  - `password` — required, non-empty (no length rule on login — the account may
    predate any rule).
  - On a missing field OR a bad email OR a wrong password, re-render
    `login.html` with the **same generic** message (e.g. "Incorrect email or
    password.") — do not reveal whether the email exists. Return HTTP 200, do
    not `abort()`.
  - On success, set `session["user_id"]` and `session["user_name"]` and
    `redirect(url_for("landing"))`.
- `logout()` uses `session.clear()` and redirects; it must not error when no one
  is logged in.
- `app.secret_key` must be set before any request uses `session`.
- Do not touch the Step 4+ stub routes (`/profile`, `/expenses/*`) — they stay
  raw-string stubs. `/profile` is still Step 4; do not add a login guard to it
  here.

## Definition of done
- [ ] `GET /login` still renders the form as before, with the email field
      autofocused.
- [ ] Submitting the seeded credentials (`demo@spendly.com` / `demo123`) sets a
      session cookie and redirects (302) to `/`.
- [ ] After a successful login the navbar shows the user's name and a "Sign out"
      link instead of "Sign in" / "Get started".
- [ ] Submitting a wrong password, an unknown email, or a blank field re-renders
      `login.html` with one visible generic error and sets no session cookie.
- [ ] The error message is identical for "unknown email" and "wrong password"
      (no account enumeration).
- [ ] On a login error the email field keeps the submitted value; the password
      field is always empty.
- [ ] `GET /logout` clears the session and redirects (302) to `/`; visiting it
      while logged out also just redirects to `/` with no error.
- [ ] The form `action`, the "Create one free" link, and the navbar "Sign out"
      link all use `url_for()` — no hardcoded paths remain in `login.html` or the
      nav block of `base.html`.
- [ ] No SQL lives in `app.py`; `verify_credentials()` is in `database/db.py`,
      reuses the parameterised `get_user_by_email()`, and checks the hash with
      `check_password_hash`.
- [ ] `pytest tests/test_login.py` passes, covering: successful login, wrong
      password, unknown email, blank field, and logout clearing the session.
- [ ] `python app.py` starts on port 5001 with no errors.
