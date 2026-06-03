from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticket Review Service")

@app.post("/internal/generate-tickets", status_code=201)
def generate_tickets(data: schemas.TicketGenerate, db: Session = Depends(get_db)):
    tickets = []
    for i in range(data.quantity):
        ticket = models.Ticket(
            booking_id=data.booking_id,
            attendee_id=data.attendee_id,
            event_id=data.event_id,
            seat_number=f"GA-{i+1}"
        )
        db.add(ticket)
        tickets.append(ticket)
    db.commit()
    return {"message": f"{data.quantity} tickets generated successfully"}

@app.get("/tickets", response_model=List[schemas.TicketResponse])
def get_tickets(attendee_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Ticket)
    if attendee_id:
        query = query.filter(models.Ticket.attendee_id == attendee_id)
    return query.all()

@app.get("/tickets/{id}", response_model=schemas.TicketResponse)
def get_ticket(id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/checkin/{ticket_code}")
def checkin_ticket(ticket_code: str, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_code == ticket_code).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status == "CHECKED_IN":
        raise HTTPException(status_code=400, detail="Ticket already checked in")
    
    ticket.status = "CHECKED_IN"
    ticket.checked_in_at = datetime.datetime.utcnow()
    db.commit()
    return {"message": "Check-in successful", "ticket_id": ticket.ticket_id}

@app.post("/reviews", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Check if user has a paid ticket for this event
    # For simplicity, we just check if they have a ticket for the event.
    ticket = db.query(models.Ticket).filter(
        models.Ticket.attendee_id == review.attendee_id,
        models.Ticket.event_id == review.event_id
    ).first()

    if not ticket:
        raise HTTPException(status_code=400, detail="Must have a ticket to review this event")

    db_review = models.EventReview(**review.model_dump())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/reviews/{event_id}", response_model=List[schemas.ReviewResponse])
def get_reviews(event_id: int, db: Session = Depends(get_db)):
    return db.query(models.EventReview).filter(models.EventReview.event_id == event_id).all()
