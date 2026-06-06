"""
TicketHub — Seed both databases with sample data.

Usage:
    python seed.py

Creates:
    - 1 admin user + 2 regular users
    - 6 sample events
    - A few sample bookings (with PayVault transactions)
    - A couple of reviews
"""

import os
import sys
import sqlite3

# Ensure emoji/unicode prints correctly on Windows consoles
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def seed_tickethub():
    """Seed the TicketHub Core database."""
    db_path = os.path.join(BASE_DIR, "tickethub_core", "tickethub_db.sqlite")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        print("  ⚠️  TicketHub DB already has data. Skipping seed.")
        conn.close()
        return

    now = datetime.now(timezone.utc)

    # ---- Users ----
    users = [
        ("admin", "admin@tickethub.com", generate_password_hash("admin123"), True),
        ("john_doe", "john@example.com", generate_password_hash("password"), False),
        ("jane_smith", "jane@example.com", generate_password_hash("password"), False),
    ]
    c.executemany(
        "INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
        [(u[0], u[1], u[2], u[3], now.isoformat()) for u in users],
    )
    print("  ✓ Created 3 users (admin/admin123, john_doe/password, jane_smith/password)")

    # ---- Events ----
    events = [
        (
            "Neon Nights Music Festival",
            "An electrifying night of EDM, house, and techno music featuring world-renowned DJs. Laser shows, immersive visuals, and an unforgettable atmosphere.",
            (now + timedelta(days=14)).isoformat(),
            "Crypto.com Arena, Los Angeles",
            89.99,
            500,
            485,
            None,
        ),
        (
            "TechConnect Summit 2026",
            "The premier technology conference bringing together industry leaders, innovators, and developers. Featuring keynotes, workshops, and networking sessions.",
            (now + timedelta(days=30)).isoformat(),
            "Moscone Center, San Francisco",
            299.99,
            1000,
            823,
            None,
        ),
        (
            "Stand-Up Comedy Night",
            "An evening of laughs with top comedians from around the country. Expect sharp wit, hilarious observations, and non-stop entertainment.",
            (now + timedelta(days=7)).isoformat(),
            "The Comedy Store, Hollywood",
            45.00,
            200,
            156,
            None,
        ),
        (
            "Artisan Food & Wine Expo",
            "Discover gourmet food, premium wines, and craft beverages from local and international artisans. Live cooking demos and tasting sessions included.",
            (now + timedelta(days=21)).isoformat(),
            "Jacob Javits Center, New York",
            75.50,
            300,
            267,
            None,
        ),
        (
            "Midnight Jazz Under the Stars",
            "An intimate open-air jazz experience featuring legendary artists performing under a canopy of stars. Wine and cocktails available.",
            (now + timedelta(days=10)).isoformat(),
            "Hollywood Bowl, Los Angeles",
            120.00,
            150,
            98,
            None,
        ),
        (
            "Startup Pitch Battle Royale",
            "Watch 20 innovative startups pitch their ideas to a panel of venture capitalists. Network, learn, and maybe discover the next unicorn.",
            (now + timedelta(days=45)).isoformat(),
            "WeWork HQ, Austin",
            35.00,
            400,
            380,
            None,
        ),
    ]
    c.executemany(
        "INSERT INTO events (name, description, date, location, price, total_seats, available_seats, image_url, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(*e, now.isoformat()) for e in events],
    )
    print(f"  ✓ Created {len(events)} events")

    # ---- Bookings ----
    bookings = [
        (2, 1, 2, 179.98, "confirmed", 1, now.isoformat()),  # john → Neon Nights x2
        (3, 3, 1, 45.00, "confirmed", 2, now.isoformat()),  # jane → Comedy Night x1
        (2, 5, 2, 240.00, "confirmed", 3, now.isoformat()),  # john → Jazz x2
    ]
    c.executemany(
        "INSERT INTO bookings (user_id, event_id, quantity, total_price, status, transaction_id, booked_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        bookings,
    )
    print(f"  ✓ Created {len(bookings)} bookings")

    # ---- Reviews ----
    reviews = [
        (2, 1, 5, "Absolutely incredible experience! The sound quality was amazing and the visuals were out of this world.", now.isoformat()),
        (3, 3, 4, "Great comedians! Had a fantastic time. Would love to come back.", now.isoformat()),
    ]
    c.executemany(
        "INSERT INTO reviews (user_id, event_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
        reviews,
    )
    print(f"  ✓ Created {len(reviews)} reviews")

    conn.commit()
    conn.close()


def seed_payvault():
    """Seed the PayVault database."""
    db_path = os.path.join(BASE_DIR, "payvault", "payvault_db.sqlite")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM transactions")
    if c.fetchone()[0] > 0:
        print("  ⚠️  PayVault DB already has data. Skipping seed.")
        conn.close()
        return

    now = datetime.now(timezone.utc)

    transactions = [
        (1, 179.98, "USD", "confirmed", "credit_card", now.isoformat(), now.isoformat()),
        (2, 45.00, "USD", "confirmed", "credit_card", now.isoformat(), now.isoformat()),
        (3, 240.00, "USD", "confirmed", "credit_card", now.isoformat(), now.isoformat()),
    ]
    c.executemany(
        "INSERT INTO transactions (booking_id, amount, currency, status, payment_method, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        transactions,
    )
    print(f"  ✓ Created {len(transactions)} transactions")

    conn.commit()
    conn.close()


def main():
    print()
    print("=" * 60)
    print("  🌱  TicketHub — Seeding Databases")
    print("=" * 60)
    print()

    # First, ensure the databases exist by importing the apps
    print("  📦 Initializing databases...")

    # Initialize TicketHub Core DB
    sys.path.insert(0, os.path.join(BASE_DIR, "tickethub_core"))
    from importlib import import_module

    core_app_module = import_module("app")
    with core_app_module.app.app_context():
        core_app_module.db.create_all()
    sys.path.pop(0)

    # Initialize PayVault DB
    sys.path.insert(0, os.path.join(BASE_DIR, "payvault"))
    # Need to reload to avoid module name conflicts
    if "models" in sys.modules:
        del sys.modules["models"]
    if "app" in sys.modules:
        del sys.modules["app"]
    pv_app_module = import_module("app")
    with pv_app_module.app.app_context():
        pv_app_module.db.create_all()
    sys.path.pop(0)

    print("  ✓ Databases initialized")
    print()

    print("  📝 Seeding TicketHub Core...")
    seed_tickethub()
    print()

    print("  📝 Seeding PayVault...")
    seed_payvault()
    print()

    print("=" * 60)
    print("  ✅ Seeding complete!")
    print()
    print("  Login credentials:")
    print("  ┌──────────────────────────────────────┐")
    print("  │  Admin:  admin / admin123             │")
    print("  │  User:   john_doe / password          │")
    print("  │  User:   jane_smith / password        │")
    print("  └──────────────────────────────────────┘")
    print()


if __name__ == "__main__":
    main()
