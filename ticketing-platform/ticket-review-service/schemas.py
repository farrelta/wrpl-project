from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketGenerate(BaseModel):
    booking_id: int
    attendee_id: int
    event_id: int
    quantity: int

class TicketResponse(BaseModel):
    ticket_id: int
    booking_id: int
    attendee_id: int
    event_id: int
    ticket_code: str
    seat_number: Optional[str] = None
    status: str
    issued_at: datetime
    checked_in_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    event_id: int
    attendee_id: int
    rating: float
    comment: str

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    review_id: int
    created_at: datetime
    class Config:
        from_attributes = True
