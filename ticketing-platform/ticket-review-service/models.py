from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from database import Base
import datetime
import uuid

def generate_ticket_code():
    return str(uuid.uuid4())[:10].upper()

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, index=True)
    attendee_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    ticket_code = Column(String(50), default=generate_ticket_code, unique=True, index=True)
    seat_number = Column(String(50), nullable=True)
    status = Column(String(50), default="ISSUED") # ISSUED, CHECKED_IN
    issued_at = Column(DateTime, default=datetime.datetime.utcnow)
    checked_in_at = Column(DateTime, nullable=True)

class EventReview(Base):
    __tablename__ = "event_reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, index=True)
    attendee_id = Column(Integer, index=True)
    rating = Column(Float)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
