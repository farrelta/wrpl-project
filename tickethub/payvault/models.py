"""PayVault — Database models."""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Transaction(db.Model):
    """Represents a payment transaction linked to a booking."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending | confirmed | failed | refunded
    payment_method = db.Column(db.String(50), nullable=False, default="credit_card")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Serialize transaction to a dictionary."""
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
