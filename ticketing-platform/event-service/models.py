from sqlalchemy import Column, Integer, String, Float, DateTime, Time, Date
from database import Base
import datetime

class Venue(Base):
    __tablename__ = "venues"

    venue_id = Column(Integer, primary_key=True, index=True)
    venue_name = Column(String(255), index=True)
    city = Column(String(100))
    address = Column(String(255))
    capacity = Column(Integer)
    venue_type = Column(String(50))

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, index=True)
    venue_id = Column(Integer, index=True)
    event_name = Column(String(255), index=True)
    category = Column(String(100))
    event_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    price = Column(Float)
    quota = Column(Integer)
    tickets_sold = Column(Integer, default=0)
    status = Column(String(50), default="UPCOMING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
