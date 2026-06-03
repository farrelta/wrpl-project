from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import requests

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking Payment Service")

EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://localhost:8002")
TICKET_SERVICE_URL = os.getenv("TICKET_SERVICE_URL", "http://localhost:8004")

@app.post("/bookings", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    if booking.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    # Fetch event details
    try:
        response = requests.get(f"{EVENT_SERVICE_URL}/events/{booking.event_id}")
        response.raise_for_status()
        event_data = response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=400, detail="Could not fetch event information")

    if event_data['status'] != "UPCOMING":
        raise HTTPException(status_code=400, detail="Event is not upcoming")

    available_quota = event_data['quota'] - event_data['tickets_sold']
    if booking.quantity > available_quota:
        raise HTTPException(status_code=400, detail="Cannot exceed quota")

    total_price = booking.quantity * event_data['price']

    db_booking = models.Booking(
        attendee_id=booking.attendee_id,
        event_id=booking.event_id,
        quantity=booking.quantity,
        total_price=total_price,
        booking_status="PENDING"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    return db_booking

@app.get("/bookings", response_model=List[schemas.BookingResponse])
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Booking).offset(skip).limit(limit).all()

@app.get("/bookings/{id}", response_model=schemas.BookingResponse)
def get_booking(id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.post("/payments", response_model=schemas.PaymentResponse)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == payment.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.booking_status == "PAID":
        raise HTTPException(status_code=400, detail="Booking is already paid")

    # Update event tickets sold
    try:
        response = requests.get(f"{EVENT_SERVICE_URL}/events/{booking.event_id}")
        response.raise_for_status()
        event_data = response.json()
        new_tickets_sold = event_data['tickets_sold'] + booking.quantity
        requests.put(f"{EVENT_SERVICE_URL}/events/{booking.event_id}", json={"tickets_sold": new_tickets_sold})
    except requests.exceptions.RequestException:
        pass # Handle properly in production

    # Generate tickets
    try:
        requests.post(f"{TICKET_SERVICE_URL}/internal/generate-tickets", json={
            "booking_id": booking.booking_id,
            "attendee_id": booking.attendee_id,
            "event_id": booking.event_id,
            "quantity": booking.quantity
        })
    except requests.exceptions.RequestException as e:
        print(f"Failed to generate tickets: {e}")
        pass # Handle properly in production

    db_payment = models.Payment(
        booking_id=payment.booking_id,
        payment_method=payment.payment_method,
        amount=booking.total_price,
        payment_status="SUCCESS"
    )
    db.add(db_payment)
    
    booking.booking_status = "PAID"
    
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

@app.get("/payments", response_model=List[schemas.PaymentResponse])
def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Payment).offset(skip).limit(limit).all()
