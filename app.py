import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "newsapp_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "newsapp.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database.sql")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def row_to_dict(row):
    if row is None:
        return None
    data = dict(row)
    if "premium" in data:
        data["premium"] = bool(data["premium"])
    if "is_admin" in data:
        data["is_admin"] = bool(data["is_admin"])
    else:
        data["is_admin"] = False
    if "author" not in data or not data["author"]:
        data["author"] = "Daily Digest Editorial"
    if "image_url" in data and data["image_url"]:
        data["image_url"] = data["image_url"].strip()
    else:
        data["image_url"] = None
    return data


def rows_to_dicts(rows):
    return [row_to_dict(r) for r in rows]


def init_db_if_needed():
    if os.path.exists(DB_PATH):
        return
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError("database.sql not found in project root.")
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())


def ensure_user_admin_setup():
    with get_db_connection() as conn:
        columns = conn.execute("PRAGMA table_info(users)").fetchall()
        column_names = {c["name"] for c in columns}
        if "is_admin" not in column_names:
            conn.execute(
                "ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))"
            )

        # Keep john_doe as admin for testing as requested.
        conn.execute("UPDATE users SET is_admin = 1 WHERE username = ?", ("john_doe",))
        conn.commit()


def ensure_article_author_setup():
    with get_db_connection() as conn:
        columns = conn.execute("PRAGMA table_info(articles)").fetchall()
        column_names = {c["name"] for c in columns}
        if "author" not in column_names:
            conn.execute(
                "ALTER TABLE articles ADD COLUMN author TEXT NOT NULL DEFAULT 'Daily Digest Editorial'"
            )

        conn.execute(
            """
            UPDATE articles
            SET author = 'Daily Digest Editorial'
            WHERE author IS NULL OR TRIM(author) = ''
            """
        )
        conn.commit()


def ensure_article_image_setup():
    with get_db_connection() as conn:
        columns = conn.execute("PRAGMA table_info(articles)").fetchall()
        column_names = {c["name"] for c in columns}
        if "image_url" not in column_names:
            conn.execute("ALTER TABLE articles ADD COLUMN image_url TEXT")
            conn.commit()


def get_user(user_id):
    if not user_id:
        return None
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return row_to_dict(row)


def get_article(article_id):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    return row_to_dict(row)


def get_all_articles(category="All"):
    with get_db_connection() as conn:
        if category == "All":
            rows = conn.execute("SELECT * FROM articles ORDER BY id").fetchall()
        else:
            rows = conn.execute("SELECT * FROM articles WHERE category = ? ORDER BY id", (category,)).fetchall()
    return rows_to_dicts(rows)


def get_all_categories():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM articles ORDER BY category").fetchall()
    return ["All"] + [r["category"] for r in rows]


def get_all_users(limit=None):
    query = "SELECT * FROM users ORDER BY id"
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
    with get_db_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows_to_dicts(rows)


def article_stats(article_id):
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type = 'View' THEN 1 ELSE 0 END), 0) AS views,
                COALESCE(SUM(CASE WHEN type = 'Like' THEN 1 ELSE 0 END), 0) AS likes,
                COALESCE(SUM(CASE WHEN type = 'Bookmark' THEN 1 ELSE 0 END), 0) AS bookmarks,
                COALESCE(SUM(CASE WHEN type = 'Share' THEN 1 ELSE 0 END), 0) AS shares
            FROM interactions
            WHERE article_id = ?
            """,
            (article_id,),
        ).fetchone()
    return dict(row)


def get_all_article_stats():
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                a.id AS article_id,
                COALESCE(SUM(CASE WHEN i.type = 'View' THEN 1 ELSE 0 END), 0) AS views,
                COALESCE(SUM(CASE WHEN i.type = 'Like' THEN 1 ELSE 0 END), 0) AS likes,
                COALESCE(SUM(CASE WHEN i.type = 'Bookmark' THEN 1 ELSE 0 END), 0) AS bookmarks,
                COALESCE(SUM(CASE WHEN i.type = 'Share' THEN 1 ELSE 0 END), 0) AS shares
            FROM articles a
            LEFT JOIN interactions i ON i.article_id = a.id
            GROUP BY a.id
            """
        ).fetchall()
    return {
        r["article_id"]: {
            "views": r["views"],
            "likes": r["likes"],
            "bookmarks": r["bookmarks"],
            "shares": r["shares"],
        }
        for r in rows
    }


def get_trending_articles(limit=5):
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT a.*
            FROM articles a
            LEFT JOIN interactions i ON i.article_id = a.id
            GROUP BY a.id
            ORDER BY COALESCE(SUM(CASE WHEN i.type IN ('View', 'Like') THEN 1 ELSE 0 END), 0) DESC, a.id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return rows_to_dicts(rows)


def search_articles(keyword, category="All"):
    """Search articles by keyword in title, content, author, and tags.
    Optionally filter by category."""
    keyword_pattern = f"%{keyword}%"
    with get_db_connection() as conn:
        if category == "All":
            rows = conn.execute(
                """
                SELECT * FROM articles
                WHERE title LIKE ? OR content LIKE ? OR author LIKE ? OR tags LIKE ?
                ORDER BY id
                """,
                (keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM articles
                WHERE category = ? AND (title LIKE ? OR content LIKE ? OR author LIKE ? OR tags LIKE ?)
                ORDER BY id
                """,
                (category, keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern),
            ).fetchall()
    return rows_to_dicts(rows)


def user_interacted(user_id, article_id, itype):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM interactions WHERE user_id = ? AND article_id = ? AND type = ? LIMIT 1",
            (user_id, article_id, itype),
        ).fetchone()
    return row is not None


def current_user():
    uid = session.get("user_id")
    return get_user(uid) if uid else None


@app.route("/")
def index():
    category = request.args.get("category", "All")
    filtered = get_all_articles(category=category)
    categories = get_all_categories()
    trending = get_trending_articles(limit=5)
    stats = get_all_article_stats()
    return render_template(
        "index.html",
        articles=filtered,
        categories=categories,
        current_category=category,
        trending=trending,
        stats=stats,
        user=current_user(),
        all_users=get_all_users(),
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "All")
    categories = get_all_categories()
    trending = get_trending_articles(limit=5)
    stats = get_all_article_stats()
    
    if query:
        results = search_articles(query, category=category)
    else:
        results = []
    
    return render_template(
        "search.html",
        query=query,
        category=category,
        articles=results,
        categories=categories,
        current_category=category,
        trending=trending,
        stats=stats,
        user=current_user(),
        all_users=get_all_users(),
    )


@app.route("/article/<int:article_id>")
def article_detail(article_id):
    article = get_article(article_id)
    if not article:
        return redirect(url_for("index"))

    user = current_user()
    if article["premium"] and (not user or not user["premium"]):
        return render_template("paywall.html", article=article, user=user)

    if user and not user_interacted(user["id"], article_id, "View"):
        with get_db_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO interactions (user_id, article_id, type) VALUES (?, ?, ?)",
                (user["id"], article_id, "View"),
            )
            conn.commit()

    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.id,
                c.article_id,
                c.user_id,
                c.content,
                c.timestamp,
                u.id AS author_id,
                u.username AS author_username,
                u.email AS author_email,
                u.preferences AS author_preferences,
                u.premium AS author_premium
            FROM comments c
            LEFT JOIN users u ON u.id = c.user_id
            WHERE c.article_id = ?
            ORDER BY c.id ASC
            """,
            (article_id,),
        ).fetchall()

    article_comments = []
    for r in rows:
        comment = {
            "id": r["id"],
            "article_id": r["article_id"],
            "user_id": r["user_id"],
            "content": r["content"],
            "timestamp": r["timestamp"],
            "author": None,
        }
        if r["author_id"] is not None:
            comment["author"] = {
                "id": r["author_id"],
                "username": r["author_username"],
                "email": r["author_email"],
                "preferences": r["author_preferences"],
                "premium": bool(r["author_premium"]),
            }
        article_comments.append(comment)

    stats = article_stats(article_id)
    article_paragraphs = [
        p.strip() for p in re.split(r"\r?\n\s*\r?\n", article["content"].strip()) if p.strip()
    ]
    user_likes = bool(user and user_interacted(user["id"], article_id, "Like"))
    user_bookmarks = bool(user and user_interacted(user["id"], article_id, "Bookmark"))

    return render_template(
        "article.html",
        article=article,
        article_paragraphs=article_paragraphs,
        comments=article_comments,
        stats=stats,
        user=user,
        user_likes=user_likes,
        user_bookmarks=user_bookmarks,
    )


@app.route("/interact/<int:article_id>/<itype>", methods=["POST"])
def interact(article_id, itype):
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    allowed_types = {"View", "Like", "Bookmark", "Share"}
    if itype not in allowed_types:
        return redirect(url_for("article_detail", article_id=article_id))

    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM interactions WHERE user_id = ? AND article_id = ? AND type = ?",
            (user["id"], article_id, itype),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM interactions WHERE id = ?", (existing["id"],))
        else:
            conn.execute(
                "INSERT INTO interactions (user_id, article_id, type) VALUES (?, ?, ?)",
                (user["id"], article_id, itype),
            )
        conn.commit()

    return redirect(url_for("article_detail", article_id=article_id))


@app.route("/comment/<int:article_id>", methods=["POST"])
def post_comment(article_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    content = request.form.get("content", "").strip()
    if content:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO comments (article_id, user_id, content, timestamp) VALUES (?, ?, ?, ?)",
                (article_id, user["id"], content, datetime.now().strftime("%Y-%m-%d %H:%M")),
            )
            conn.commit()

    return redirect(url_for("article_detail", article_id=article_id))


@app.route("/unlock/<int:article_id>", methods=["POST"])
def unlock(article_id):
    # Keep endpoint safe if called directly; premium articles still require active premium.
    article = get_article(article_id)
    user = current_user()
    if not article:
        return redirect(url_for("index"))
    if article["premium"] and (not user or not user["premium"]):
        return render_template("paywall.html", article=article, user=user)
    return redirect(url_for("article_detail", article_id=article_id))


@app.route("/pricing")
def pricing():
    plans = [
        {
            "name": "Free",
            "price": "0",
            "period": "forever",
            "description": "Basic access to free articles only.",
            "old_price": None,
            "highlight": False,
        },
        {
            "name": "Weekly",
            "price": "25,000",
            "period": "per week",
            "description": "Unlimited premium reading for 7 days.",
            "old_price": None,
            "highlight": False,
        },
        {
            "name": "Monthly",
            "price": "50,000",
            "period": "per month",
            "description": "Best value for regular readers.",
            "old_price": "100,000",
            "highlight": True,
        },
        {
            "name": "Annual",
            "price": "450,000",
            "period": "per year",
            "description": "Full-year premium access with the largest discount.",
            "old_price": "900,000",
            "highlight": False,
        },
    ]
    return render_template("pricing.html", plans=plans, user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()
        user = row_to_dict(row)
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        error = "Invalid username or password."
    return render_template("login.html", error=error, user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        preferences = request.form.get("preferences", "").strip()

        if not username or not email or not password:
            error = "Username, email, and password are required."
        else:
            try:
                with get_db_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO users (username, email, password, preferences, premium, is_admin)
                        VALUES (?, ?, ?, ?, 0, 0)
                        """,
                        (username, email, password, preferences),
                    )
                    conn.commit()
            except sqlite3.IntegrityError:
                error = "Username or email already exists."

        if not error:
            with get_db_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
            user = row_to_dict(row)
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

    return render_template("register.html", error=error, user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard/article/<int:article_id>/image", methods=["POST"])
def update_article_image(article_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    if not user.get("is_admin", False):
        return redirect(url_for("index"))

    article = get_article(article_id)
    if not article:
        return redirect(url_for("dashboard", image_update="not_found"))

    image_url = request.form.get("image_url", "").strip()
    image_value = image_url or None

    with get_db_connection() as conn:
        conn.execute(
            "UPDATE articles SET image_url = ? WHERE id = ?",
            (image_value, article_id),
        )
        conn.commit()

    return redirect(url_for("dashboard", image_update="saved"))


@app.route("/dashboard/articles/new", methods=["GET", "POST"])
def create_article():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    if not user.get("is_admin", False):
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "").strip()
        author = request.form.get("author", "").strip()
        tags = request.form.get("tags", "").strip()
        image_url = request.form.get("image_url", "").strip()
        date = request.form.get("date", "").strip()
        premium = 1 if request.form.get("premium") else 0

        # Validation
        if not title or not content or not category or not date:
            error = "Title, content, category, and date are required."
        else:
            try:
                with get_db_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO articles (title, content, category, author, tags, image_url, date, premium)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            title,
                            content,
                            category,
                            author if author else "Daily Digest Editorial",
                            tags if tags else "",
                            image_url if image_url else None,
                            date,
                            premium,
                        ),
                    )
                    conn.commit()
                return redirect(url_for("dashboard", article_created="success"))
            except sqlite3.Error as e:
                error = f"Error creating article: {str(e)}"

    from datetime import date as date_type
    categories = get_all_categories()
    today = date_type.today().isoformat()

    return render_template(
        "add-article.html",
        user=user,
        categories=categories,
        today_date=today,
        error=error,
    )


@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    if not user.get("is_admin", False):
        return redirect(url_for("index"))

    article_created = request.args.get("article_created")
    image_update = request.args.get("image_update")

    articles = get_all_articles(category="All")
    all_stats = get_all_article_stats()

    with get_db_connection() as conn:
        comment_rows = conn.execute(
            "SELECT article_id, COUNT(*) AS count FROM comments GROUP BY article_id"
        ).fetchall()
        all_comment_counts = {r["article_id"]: r["count"] for r in comment_rows}

        users = rows_to_dicts(conn.execute("SELECT * FROM users ORDER BY id").fetchall())

        interaction_rows = conn.execute(
            "SELECT user_id, COUNT(*) AS count FROM interactions GROUP BY user_id"
        ).fetchall()
        user_interaction_counts = {r["user_id"]: r["count"] for r in interaction_rows}

        user_comment_rows = conn.execute(
            "SELECT user_id, COUNT(*) AS count FROM comments GROUP BY user_id"
        ).fetchall()
        user_comment_counts = {r["user_id"]: r["count"] for r in user_comment_rows}

        total_interactions = conn.execute("SELECT COUNT(*) AS c FROM interactions").fetchone()["c"]
        total_comments = conn.execute("SELECT COUNT(*) AS c FROM comments").fetchone()["c"]

    for a in articles:
        if a["id"] not in all_comment_counts:
            all_comment_counts[a["id"]] = 0

    user_stats = []
    for u in users:
        user_stats.append(
            {
                "user": u,
                "interactions": user_interaction_counts.get(u["id"], 0),
                "comments": user_comment_counts.get(u["id"], 0),
            }
        )

    return render_template(
        "dashboard.html",
        articles=articles,
        all_stats=all_stats,
        all_comment_counts=all_comment_counts,
        user_stats=user_stats,
        total_interactions=total_interactions,
        total_comments=total_comments,
        article_created=article_created,
        image_update=image_update,
        user=user,
    )


init_db_if_needed()
ensure_user_admin_setup()
ensure_article_author_setup()
ensure_article_image_setup()


if __name__ == "__main__":
    app.run(debug=True)
