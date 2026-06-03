from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizerBase(BaseModel):
    company_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    organizer_type: Optional[str] = None

class OrganizerCreate(OrganizerBase):
    pass

class OrganizerResponse(OrganizerBase):
    organizer_id: int
    rating: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AttendeeBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    birth_date: Optional[str] = None

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeResponse(AttendeeBase):
    attendee_id: int
    registered_at: datetime

    class Config:
        from_attributes = True
