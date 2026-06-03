from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
import datetime
import uuid

def generate_booking_code():
    return str(uuid.uuid4())[:8].upper()

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(50), default=generate_booking_code, unique=True, index=True)
    attendee_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    quantity = Column(Integer)
    total_price = Column(Float)
    booking_status = Column(String(50), default="PENDING") # PENDING, PAID, CANCELLED
    booked_at = Column(DateTime, default=datetime.datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, index=True)
    payment_method = Column(String(50))
    amount = Column(Float)
    payment_status = Column(String(50), default="SUCCESS")
    paid_at = Column(DateTime, default=datetime.datetime.utcnow)
