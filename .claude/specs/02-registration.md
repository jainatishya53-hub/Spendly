# Spec: Registration

## Overview
This step turns the existing registration page into a working sign-up flow. Today
`GET /register` only renders `register.html`; the form POSTs to `/register` but no
route handles it. This feature adds `POST /register` handling: validate the
submitted name, email, and password; hash the password with werkzeug; insert a new
row into the `users` table; and redirect the new user to the login page. It sits
directly on top of Step 1 (database setup) and is the first half of authentication —
Step 3 (login/logout) will consume the accounts created here.

## Depends on
- **Step 1 — Database setup** — `users` table, `get_db()`, `init_db()`, `seed_db()`
  must all exist and work (they do).

## Routes
- `GET /register` — render the registration form — public *(already implemented; will
  be merged into a single `methods=["GET", "POST"]` handler)*
- `POST /register` — validate input, create the user, redirect to `/login` on
  success; re-render `register.html` with an `error` message on failure — public

## Database changes
No database changes. The existing `users` schema from Step 1 already covers this:
`name`, `email` (UNIQUE, NOT NULL), `password_hash`, `created_at` (default). All
inserts go through a new helper in `database/db.py` — no inline SQL in the route.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html`
    - Change `<form method="POST" action="/register">` to
      `action="{{ url_for('register') }}"` (no hardcoded URLs).
    - Keep the existing `{% if error %}<div class="auth-error">` block — it is
      already styled in `style.css` and will display server-side validation errors.
    - Repopulate `name` and `email` inputs with submitted values on error
      (`value="{{ name or '' }}"`) so the user does not retype them.

## Files to change
- `app.py` — replace the `GET`-only `register()` route with a
  `methods=["GET", "POST"]` handler that validates input, calls the new DB helper,
  and redirects or re-renders. Add `redirect`, `url_for`, `request` to the
  `flask` import.
- `database/db.py` — add `create_user(name, email, password_hash)` and
  `get_user_by_email(email)` helpers using parameterized queries.
- `templates/register.html` — see Templates section.

## Files to create
- `.claude/specs/02-registration.md` — this spec.
- `tests/test_registration.py` — pytest coverage for the flow (see Definition of
  done).

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` is already imported
in `database/db.py`; `pytest` / `pytest-flask` are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only (`?` placeholders) — never f-strings or `.format()` in
  SQL.
- Passwords hashed with `werkzeug.security.generate_password_hash`; never store the
  raw password. Do not log the password.
- All DB access lives in `database/db.py` — the route calls helpers, it does not open
  connections or write SQL.
- Use CSS variables — never hardcode hex values (the `.auth-error` style already
  exists; no new CSS is expected).
- All templates extend `base.html` (`register.html` already does).
- Use `url_for()` for every internal link and the form `action`.
- Route function keeps one responsibility per path: GET renders, POST processes.
- Validation rules:
  - `name` — required, stripped, non-empty.
  - `email` — required, stripped, contains `@`, lowercased before storage.
  - `password` — required, minimum 8 characters (matches the form's
    "Min. 8 characters" hint).
  - Duplicate email — check `get_user_by_email()` first; also catch
    `sqlite3.IntegrityError` from the UNIQUE constraint as a backstop, and show a
    friendly "An account with that email already exists" error.
- On any validation failure, re-render `register.html` with `error` set and the
  previously entered `name` / `email`; return HTTP 200 (form redisplay), do not
  `abort()`.
- On success, `redirect(url_for("login"))`. Do not auto-login — sessions arrive in
  Step 3.
- Do not touch the Step 3+ stub routes (`/logout`, `/profile`, `/expenses/*`).

## Definition of done
- [ ] `GET /register` still renders the form exactly as before.
- [ ] Submitting valid name + email + 8char password creates exactly one new row
      in `users` with a non-plaintext `password_hash`, then redirects to `/login`.
- [ ] Submitting an email that already exists (e.g. `demo@spendly.com`) re-renders
      the form with a visible error and creates no new row.
- [ ] Submitting a blank name, a malformed email, or a password shorter than 8
      characters re-renders the form with a visible error and creates no new row.
- [ ] On a validation error the name and email fields keep the submitted values.
- [ ] The form `action` and the "Sign in" link both use `url_for()` — no hardcoded
      paths remain in `register.html`.
- [ ] No SQL lives in `app.py`; `create_user` / `get_user_by_email` are in
      `database/db.py` and use `?` placeholders.
- [ ] `pytest tests/test_registration.py` passes, covering: successful signup,
      duplicate email, and each validation failure.
- [ ] `python app.py` starts on port 5001 with no errors.
