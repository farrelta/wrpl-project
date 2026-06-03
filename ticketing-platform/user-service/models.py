from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
import datetime

class Organizer(Base):
    __tablename__ = "organizers"

    organizer_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    city = Column(String(100))
    organizer_type = Column(String(50))
    rating = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Attendee(Base):
    __tablename__ = "attendees"

    attendee_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    city = Column(String(100))
    birth_date = Column(String(50)) # Kept simple as String (YYYY-MM-DD)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
