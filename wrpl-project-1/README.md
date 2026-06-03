# The Daily Digest — News App (Flask)
Workshop ISD Group 3 · Arya, Dimas, Farrel, Filbert, Klara

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
http://127.0.0.1:5000
```

## Features
- Browse articles by category
- Read full articles (premium articles require login or ad-unlock)
- Like, Bookmark, Share interactions
- Comment system (login required)
- User authentication
- Dashboard with analytics

## Database (SQL)
The project now includes a SQL database file at `database.sql` with schema and seed data for:
- users
- articles
- comments
- interactions

The Flask app now uses SQLite directly (`newsapp.db`) instead of in-memory Python lists.

To create a local SQLite database from it:

```bash
sqlite3 newsapp.db < database.sql
```

If `newsapp.db` does not exist, the app will automatically initialize it from `database.sql` on first run.

You can then inspect and manage data with any SQLite client.

## Project Structure
```
newsapp/
├── app.py              # Flask app, routes, sample data
├── requirements.txt
└── templates/
    ├── base.html       # Shared layout
    ├── index.html      # Home / article feed
    ├── article.html    # Article detail + comments
    ├── paywall.html    # Premium article gate
    ├── login.html      # Login form
    └── dashboard.html  # Analytics dashboard
```
