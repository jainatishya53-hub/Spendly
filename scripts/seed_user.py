"""One-off script: seed a single realistic dummy Indian user.

Run with: python scripts/seed_user.py
"""
import os
import random
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash

from database.db import get_db

FIRST_NAMES = [
    "Rahul", "Amit", "Priya", "Sneha", "Vikram", "Ananya", "Rohan", "Kavya",
    "Arjun", "Divya", "Karthik", "Meera", "Suresh", "Pooja", "Anil", "Neha",
    "Rajesh", "Shreya", "Vivek", "Isha", "Manoj", "Ritu", "Sanjay", "Aditi",
    "Deepak", "Nandini", "Gaurav", "Swati", "Harish", "Lakshmi", "Nikhil",
    "Aarav", "Ishaan", "Kiran", "Vidya", "Ramesh", "Sunita", "Abhishek",
    "Preeti", "Siddharth", "Vandana",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Iyer", "Nair", "Reddy", "Menon", "Rao",
    "Patel", "Joshi", "Mehta", "Kulkarni", "Chatterjee", "Banerjee", "Das",
    "Pillai", "Naidu", "Agarwal", "Bhat", "Desai", "Kapoor", "Malhotra",
    "Chauhan", "Yadav", "Mishra", "Pandey", "Ghosh", "Rana", "Trivedi",
    "Shetty",
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com"]


def generate_user():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    number = random.randint(10, 999)
    domain = random.choice(EMAIL_DOMAINS)
    email = f"{first.lower()}.{last.lower()}{number}@{domain}"
    return name, email


def main():
    conn = get_db()
    try:
        while True:
            name, email = generate_user()
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing is None:
                break

        password_hash = generate_password_hash("password123")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) "
            "VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at),
        )
        conn.commit()
        user_id = cursor.lastrowid

        print("Seeded user:")
        print(f"  id:    {user_id}")
        print(f"  name:  {name}")
        print(f"  email: {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
