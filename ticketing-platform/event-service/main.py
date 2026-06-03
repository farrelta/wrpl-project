from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Service")

@app.post("/venues", response_model=schemas.VenueResponse)
def create_venue(venue: schemas.VenueCreate, db: Session = Depends(get_db)):
    db_venue = models.Venue(**venue.model_dump())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

@app.get("/venues", response_model=List[schemas.VenueResponse])
def get_venues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Venue).offset(skip).limit(limit).all()

@app.post("/events", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events", response_model=List[schemas.EventResponse])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Event).offset(skip).limit(limit).all()

@app.get("/events/{id}", response_model=schemas.EventResponse)
def get_event(id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.event_id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.put("/events/{id}", response_model=schemas.EventResponse)
def update_event(id: int, event_update: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.event_id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

@app.delete("/events/{id}")
def delete_event(id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.event_id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}
