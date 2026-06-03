from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")

@app.post("/register-attendee", response_model=schemas.AttendeeResponse)
def register_attendee(attendee: schemas.AttendeeCreate, db: Session = Depends(get_db)):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.email == attendee.email).first()
    if db_attendee:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_attendee = models.Attendee(**attendee.model_dump())
    db.add(new_attendee)
    db.commit()
    db.refresh(new_attendee)
    return new_attendee

@app.post("/register-organizer", response_model=schemas.OrganizerResponse)
def register_organizer(organizer: schemas.OrganizerCreate, db: Session = Depends(get_db)):
    db_org = db.query(models.Organizer).filter(models.Organizer.email == organizer.email).first()
    if db_org:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_org = models.Organizer(**organizer.model_dump())
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

@app.get("/attendees", response_model=List[schemas.AttendeeResponse])
def get_attendees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Attendee).offset(skip).limit(limit).all()

@app.get("/organizers", response_model=List[schemas.OrganizerResponse])
def get_organizers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Organizer).offset(skip).limit(limit).all()

@app.get("/attendees/{id}", response_model=schemas.AttendeeResponse)
def get_attendee(id: int, db: Session = Depends(get_db)):
    attendee = db.query(models.Attendee).filter(models.Attendee.attendee_id == id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return attendee

@app.get("/organizers/{id}", response_model=schemas.OrganizerResponse)
def get_organizer(id: int, db: Session = Depends(get_db)):
    org = db.query(models.Organizer).filter(models.Organizer.organizer_id == id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return org
