import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for

from database.db import (
    create_user,
    get_db,
    get_user_by_email,
    init_db,
    seed_db,
    verify_credentials,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id") is not None:
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        error = None
        if not name:
            error = "Please enter your name."
        elif "@" not in email:
            error = "Please enter a valid email address."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif get_user_by_email(email) is not None:
            error = "An account with that email already exists."

        if error is None:
            try:
                create_user(name, email, password)
            except sqlite3.IntegrityError:
                error = "An account with that email already exists."

        if error is not None:
            return render_template(
                "register.html", error=error, name=name, email=email
            )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id") is not None:
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = None
        if email and password:
            user = verify_credentials(email, password)

        if user is None:
            return render_template(
                "login.html",
                error="Incorrect email or password.",
                email=email,
            )

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if session.get("user_id") is None:
        return redirect(url_for("login"))

    # --- Step 4: hardcoded design data; Step 5 replaces this with DB queries ---
    display_name = session.get("user_name") or "there"
    initials = "".join(part[0] for part in display_name.split()[:2]).upper() or "U"

    user = {
        "name": display_name,
        "initials": initials,
        "email": "demo@spendly.com",
        "member_since": "January 2026",
    }
    stats = {
        "total_spent": "₹48,250",
        "transaction_count": 42,
        "top_category": "Food",
    }
    transactions = [
        {"date": "Aug 28, 2026", "description": "Grocery run — DMart",
         "category": "Food",          "category_slug": "food",          "amount": "₹2,140"},
        {"date": "Aug 27, 2026", "description": "Auto to office",
         "category": "Transport",     "category_slug": "transport",     "amount": "₹90"},
        {"date": "Aug 26, 2026", "description": "Electricity bill",
         "category": "Bills",         "category_slug": "bills",         "amount": "₹1,860"},
        {"date": "Aug 25, 2026", "description": "Pharmacy — cold meds",
         "category": "Health",        "category_slug": "health",        "amount": "₹430"},
        {"date": "Aug 24, 2026", "description": "Movie night",
         "category": "Entertainment", "category_slug": "entertainment", "amount": "₹700"},
        {"date": "Aug 23, 2026", "description": "New running shoes",
         "category": "Shopping",      "category_slug": "shopping",      "amount": "₹3,499"},
    ]
    category_breakdown = [
        {"name": "Food",          "slug": "food",          "amount": "₹18,400", "percent": 40},
        {"name": "Bills",         "slug": "bills",         "amount": "₹9,600",  "percent": 20},
        {"name": "Shopping",      "slug": "shopping",      "amount": "₹7,700",  "percent": 15},
        {"name": "Transport",     "slug": "transport",     "amount": "₹5,300",  "percent": 10},
        {"name": "Entertainment", "slug": "entertainment", "amount": "₹4,100",  "percent": 10},
        {"name": "Health",        "slug": "health",        "amount": "₹3,150",  "percent": 5},
    ]

    return render_template(
        "profile.html",
        user=user, stats=stats,
        transactions=transactions,
        category_breakdown=category_breakdown,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
