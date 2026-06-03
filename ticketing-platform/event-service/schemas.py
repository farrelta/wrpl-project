from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class VenueBase(BaseModel):
    venue_name: str
    city: str
    address: str
    capacity: int
    venue_type: Optional[str] = None

class VenueCreate(VenueBase):
    pass

class VenueResponse(VenueBase):
    venue_id: int
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    organizer_id: int
    venue_id: int
    event_name: str
    category: str
    event_date: date
    start_time: time
    end_time: time
    price: float
    quota: int
    status: Optional[str] = "UPCOMING"

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    category: Optional[str] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    price: Optional[float] = None
    quota: Optional[int] = None
    tickets_sold: Optional[int] = None
    status: Optional[str] = None

class EventResponse(EventBase):
    event_id: int
    tickets_sold: int
    created_at: datetime
    class Config:
        from_attributes = True
