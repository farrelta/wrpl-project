"""
TicketHub Core — Main Application (Company 1)
Port: 5001 | DB: tickethub_db.sqlite

Full web application with user-facing UI and admin dashboard.
"""

import os
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Event, Booking, Review
from payvault_client import PayVaultClient

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "tickethub-super-secret-key-change-in-prod"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'tickethub_db.sqlite')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def admin_required(f):
    """Decorator that restricts a view to admin users only."""

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Context processor — inject current year for templates
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {"now": datetime.now(timezone.utc)}


# =========================================================================
#  PUBLIC / USER ROUTES
# =========================================================================


@app.route("/")
def index():
    """Landing page — browse all upcoming events."""
    search = request.args.get("q", "").strip()
    if search:
        events = (
            Event.query.filter(Event.name.ilike(f"%{search}%"))
            .order_by(Event.date.asc())
            .all()
        )
    else:
        events = Event.query.order_by(Event.date.asc()).all()
    return render_template("index.html", events=events, search=search)


# ---- Auth ----------------------------------------------------------------


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            flash("Username or email already taken.", "error")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---- Events & Booking ---------------------------------------------------


@app.route("/event/<int:event_id>")
def event_detail(event_id):
    """Show event details, reviews, and booking form."""
    event = Event.query.get_or_404(event_id)
    reviews = (
        Review.query.filter_by(event_id=event_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    user_has_booking = False
    user_has_reviewed = False
    if current_user.is_authenticated:
        user_has_booking = Booking.query.filter_by(
            user_id=current_user.id, event_id=event_id, status="confirmed"
        ).first() is not None
        user_has_reviewed = Review.query.filter_by(
            user_id=current_user.id, event_id=event_id
        ).first() is not None

    return render_template(
        "event_detail.html",
        event=event,
        reviews=reviews,
        user_has_booking=user_has_booking,
        user_has_reviewed=user_has_reviewed,
    )


@app.route("/event/<int:event_id>/review-booking", methods=["POST"])
@login_required
def review_booking(event_id):
    """Show booking confirmation prompt before purchasing."""
    event = Event.query.get_or_404(event_id)
    quantity = int(request.form.get("quantity", 1))

    if quantity < 1:
        flash("Quantity must be at least 1.", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    if event.available_seats < quantity:
        flash("Not enough seats available.", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    total_price = round(event.price * quantity, 2)

    return render_template("review_booking.html", event=event, quantity=quantity, total_price=total_price)


@app.route("/event/<int:event_id>/book", methods=["POST"])
@login_required
def book_event(event_id):
    """Book tickets for an event — calls PayVault to process payment."""
    event = Event.query.get_or_404(event_id)
    quantity = int(request.form.get("quantity", 1))

    if quantity < 1:
        flash("Quantity must be at least 1.", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    if event.available_seats < quantity:
        flash("Not enough seats available.", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    total_price = round(event.price * quantity, 2)

    # 1. Create booking in pending state
    booking = Booking(
        user_id=current_user.id,
        event_id=event_id,
        quantity=quantity,
        total_price=total_price,
        status="confirmed",
    )
    db.session.add(booking)
    db.session.flush()  # get booking.id before commit

    # 2. Call PayVault to create + confirm transaction
    txn = PayVaultClient.create_transaction(booking.id, total_price)
    if "error" in txn:
        db.session.rollback()
        flash(f"Payment service error: {txn['error']}", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    confirm = PayVaultClient.confirm_payment(txn["id"])
    if "error" in confirm:
        PayVaultClient.fail_payment(txn["id"])
        db.session.rollback()
        flash("Payment could not be confirmed.", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    # 3. Finalize booking
    booking.transaction_id = txn["id"]
    event.available_seats -= quantity
    db.session.commit()

    flash(f"Successfully booked {quantity} ticket(s)!", "success")
    return redirect(url_for("booking_confirmation", booking_id=booking.id))


@app.route("/booking/<int:booking_id>/confirmation")
@login_required
def booking_confirmation(booking_id):
    """Show booking confirmation page after successful booking."""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    return render_template("booking_confirmation.html", booking=booking)


@app.route("/my-bookings")
@login_required
def my_bookings():
    """List current user's bookings."""
    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booked_at.desc())
        .all()
    )
    return render_template("my_bookings.html", bookings=bookings)


@app.route("/booking/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking and request a refund via PayVault."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        abort(403)

    if booking.status != "confirmed":
        flash("This booking is already cancelled.", "warning")
        return redirect(url_for("my_bookings"))

    # Refund via PayVault
    if booking.transaction_id:
        refund = PayVaultClient.refund_payment(booking.transaction_id)
        if "error" in refund:
            flash(f"Refund error: {refund['error']}", "error")
            return redirect(url_for("my_bookings"))

    booking.status = "cancelled"
    booking.event.available_seats += booking.quantity
    db.session.commit()

    flash("Booking cancelled and refund issued.", "success")
    return redirect(url_for("my_bookings"))


# ---- Reviews -------------------------------------------------------------


@app.route("/event/<int:event_id>/review", methods=["POST"])
@login_required
def submit_review(event_id):
    """Submit a review for an event the user has attended."""
    event = Event.query.get_or_404(event_id)

    # Check that user has a confirmed booking for this event
    has_booking = Booking.query.filter_by(
        user_id=current_user.id, event_id=event_id, status="confirmed"
    ).first()
    if not has_booking:
        flash("You can only review events you have booked.", "warning")
        return redirect(url_for("event_detail", event_id=event_id))

    # Check for duplicate review
    existing = Review.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first()
    if existing:
        flash("You have already reviewed this event.", "warning")
        return redirect(url_for("event_detail", event_id=event_id))

    rating = int(request.form.get("rating", 5))
    comment = request.form.get("comment", "").strip()

    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(url_for("event_detail", event_id=event_id))

    review = Review(
        user_id=current_user.id,
        event_id=event_id,
        rating=rating,
        comment=comment,
    )
    db.session.add(review)
    db.session.commit()

    flash("Review submitted!", "success")
    return redirect(url_for("event_detail", event_id=event_id))


# =========================================================================
#  ADMIN ROUTES
# =========================================================================


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard with stats."""
    total_users = User.query.count()
    total_events = Event.query.count()
    total_bookings = Booking.query.filter_by(status="confirmed").count()
    total_revenue = (
        db.session.query(db.func.sum(Booking.total_price))
        .filter_by(status="confirmed")
        .scalar()
        or 0
    )
    total_tickets_sold = (
        db.session.query(db.func.sum(Booking.quantity))
        .filter_by(status="confirmed")
        .scalar()
        or 0
    )
    upcoming_events = (
        Event.query.filter(Event.date >= datetime.now(timezone.utc))
        .order_by(Event.date.asc())
        .limit(5)
        .all()
    )
    recent_bookings = (
        Booking.query.order_by(Booking.booked_at.desc()).limit(10).all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_events=total_events,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        total_tickets_sold=total_tickets_sold,
        upcoming_events=upcoming_events,
        recent_bookings=recent_bookings,
    )


@app.route("/admin/events")
@admin_required
def admin_events():
    """List all events for management."""
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template("admin/events.html", events=events)


@app.route("/admin/events/add", methods=["GET", "POST"])
@admin_required
def admin_add_event():
    """Add a new event."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        date_str = request.form.get("date", "")
        location = request.form.get("location", "").strip()
        price = float(request.form.get("price", 0))
        total_seats = int(request.form.get("total_seats", 0))
        image_url = request.form.get("image_url", "").strip() or None

        if not name or not date_str or not location:
            flash("Name, date, and location are required.", "error")
            return redirect(url_for("admin_add_event"))

        event = Event(
            name=name,
            description=description,
            date=datetime.fromisoformat(date_str),
            location=location,
            price=price,
            total_seats=total_seats,
            available_seats=total_seats,
            image_url=image_url,
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created!", "success")
        return redirect(url_for("admin_events"))

    return render_template("admin/event_form.html", event=None)


@app.route("/admin/events/<int:event_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_event(event_id):
    """Edit an existing event."""
    event = Event.query.get_or_404(event_id)

    if request.method == "POST":
        event.name = request.form.get("name", "").strip()
        event.description = request.form.get("description", "").strip()
        event.date = datetime.fromisoformat(request.form.get("date", ""))
        event.location = request.form.get("location", "").strip()
        event.price = float(request.form.get("price", 0))

        new_total = int(request.form.get("total_seats", event.total_seats))
        diff = new_total - event.total_seats
        event.total_seats = new_total
        event.available_seats = max(0, event.available_seats + diff)
        event.image_url = request.form.get("image_url", "").strip() or None

        db.session.commit()
        flash("Event updated!", "success")
        return redirect(url_for("admin_events"))

    return render_template("admin/event_form.html", event=event)


@app.route("/admin/events/<int:event_id>/delete", methods=["POST"])
@admin_required
def admin_delete_event(event_id):
    """Delete an event."""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("admin_events"))


@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    """View all bookings."""
    bookings = Booking.query.order_by(Booking.booked_at.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


@app.route("/admin/users")
@admin_required
def admin_users():
    """View all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(403)
def forbidden(e):
    return render_template("base.html", error_code=403, error_msg="Forbidden"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", error_code=404, error_msg="Page Not Found"), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
