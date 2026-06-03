# Multi-Company Ticketing Platform

A microservice-based ticketing platform built with FastAPI, Streamlit, MySQL, and Docker Compose.

## Architecture

The system consists of 4 backend microservices and 1 frontend app:
1. **User Service**: Manages Attendees and Organizers.
2. **Event Service**: Manages Venues and Events.
3. **Booking Payment Service**: Manages Bookings and Payments.
4. **Ticket Review Service**: Generates Tickets and Handles Reviews.
5. **API Gateway**: Reverse proxy aggregating the services.
6. **Frontend**: Streamlit multi-page application.

## Prerequisites
- Docker
- Docker Compose

## How to Run

1. Clone or navigate to the project directory.
2. Run the following command:
```bash
docker-compose up --build
```
3. Wait a few moments for the databases to initialize and the services to start.
4. Access the frontend at: [http://localhost:8501](http://localhost:8501)
5. Access the API Gateway (FastAPI docs) at: [http://localhost:8000/docs](http://localhost:8000/docs)

## Simple Flow to Test

1. Populate the database with sample data by running the provided PowerShell script:
```powershell
.\seed.ps1
```
*(This will automatically create a sample Attendee, Organizer, Venue, and Event via the API Gateway).*
2. Use the Streamlit Frontend (`http://localhost:8501`) to browse the newly created event.
3. Go to the "Booking Page" and book the event using Attendee ID `1` and Event ID `1`.
4. Go to the "Payment Page" and pay for your pending booking.
5. View your generated tickets in the "My Tickets" page.
6. Add a review on the "Review Page".
