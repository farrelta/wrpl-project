from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookingBase(BaseModel):
    attendee_id: int
    event_id: int
    quantity: int

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    booking_id: int
    booking_code: str
    total_price: float
    booking_status: str
    booked_at: datetime
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    booking_id: int
    payment_method: str

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    payment_id: int
    amount: float
    payment_status: str
    paid_at: datetime
    class Config:
        from_attributes = True
