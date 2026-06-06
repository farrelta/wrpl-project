"""
PayVault — Internal Payment API (Company 2)
Port: 5002 | DB: payvault_db.sqlite

Headless REST API consumed by TicketHub Core.
"""

import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from models import db, Transaction

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'payvault_db.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({"status": "ok", "service": "PayVault"}), 200


# ---------------------------------------------------------------------------
# Create transaction
# ---------------------------------------------------------------------------
@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    """Create a new pending transaction for a booking."""
    data = request.get_json(force=True)

    booking_id = data.get("booking_id")
    amount = data.get("amount")
    currency = data.get("currency", "USD")
    payment_method = data.get("payment_method", "credit_card")

    if booking_id is None or amount is None:
        return jsonify({"error": "booking_id and amount are required"}), 400

    txn = Transaction(
        booking_id=booking_id,
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        status="pending",
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify(txn.to_dict()), 201


# ---------------------------------------------------------------------------
# Confirm payment
# ---------------------------------------------------------------------------
@app.route("/api/transactions/<int:txn_id>/confirm", methods=["POST"])
def confirm_transaction(txn_id):
    """Mark a pending transaction as confirmed."""
    txn = Transaction.query.get_or_404(txn_id)

    if txn.status != "pending":
        return jsonify({"error": f"Cannot confirm a transaction with status '{txn.status}'"}), 400

    txn.status = "confirmed"
    txn.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(txn.to_dict()), 200


# ---------------------------------------------------------------------------
# Fail payment
# ---------------------------------------------------------------------------
@app.route("/api/transactions/<int:txn_id>/fail", methods=["POST"])
def fail_transaction(txn_id):
    """Mark a pending transaction as failed."""
    txn = Transaction.query.get_or_404(txn_id)

    if txn.status != "pending":
        return jsonify({"error": f"Cannot fail a transaction with status '{txn.status}'"}), 400

    txn.status = "failed"
    txn.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(txn.to_dict()), 200


# ---------------------------------------------------------------------------
# Refund payment
# ---------------------------------------------------------------------------
@app.route("/api/transactions/<int:txn_id>/refund", methods=["POST"])
def refund_transaction(txn_id):
    """Issue a refund for a confirmed transaction."""
    txn = Transaction.query.get_or_404(txn_id)

    if txn.status != "confirmed":
        return jsonify({"error": f"Cannot refund a transaction with status '{txn.status}'"}), 400

    txn.status = "refunded"
    txn.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(txn.to_dict()), 200


# ---------------------------------------------------------------------------
# Get transactions by booking ID
# ---------------------------------------------------------------------------
@app.route("/api/transactions/booking/<int:booking_id>", methods=["GET"])
def get_transactions_by_booking(booking_id):
    """Return all transactions associated with a given booking."""
    txns = Transaction.query.filter_by(booking_id=booking_id).order_by(
        Transaction.created_at.desc()
    ).all()
    return jsonify([t.to_dict() for t in txns]), 200


# ---------------------------------------------------------------------------
# Get single transaction
# ---------------------------------------------------------------------------
@app.route("/api/transactions/<int:txn_id>", methods=["GET"])
def get_transaction(txn_id):
    """Return a single transaction by its ID."""
    txn = Transaction.query.get_or_404(txn_id)
    return jsonify(txn.to_dict()), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
