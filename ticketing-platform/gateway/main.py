from fastapi import FastAPI, Request, Response
import httpx
import os

app = FastAPI(title="API Gateway")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://localhost:8002")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8003")
TICKET_SERVICE_URL = os.getenv("TICKET_SERVICE_URL", "http://localhost:8004")

client = httpx.AsyncClient()

async def forward_request(request: Request, target_url: str):
    method = request.method
    url = f"{target_url}{request.url.path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()
    
    # Exclude query parameters from URL because httpx adds them from params, but here we construct url fully
    # Actually request.url.path doesn't include query params. Let's include them.
    url = f"{target_url}{request.url.path}?{request.url.query}" if request.url.query else f"{target_url}{request.url.path}"

    response = await client.request(
        method,
        url,
        headers=headers,
        content=body
    )
    
    return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))

# User Service Routes
@app.api_route("/register-attendee", methods=["POST"])
@app.api_route("/register-organizer", methods=["POST"])
@app.api_route("/attendees", methods=["GET"])
@app.api_route("/attendees/{id}", methods=["GET"])
@app.api_route("/organizers", methods=["GET"])
@app.api_route("/organizers/{id}", methods=["GET"])
async def user_routes(request: Request):
    return await forward_request(request, USER_SERVICE_URL)

# Event Service Routes
@app.api_route("/venues", methods=["GET", "POST"])
@app.api_route("/events", methods=["GET", "POST"])
@app.api_route("/events/{id}", methods=["GET", "PUT", "DELETE"])
async def event_routes(request: Request):
    return await forward_request(request, EVENT_SERVICE_URL)

# Booking Payment Routes
@app.api_route("/bookings", methods=["GET", "POST"])
@app.api_route("/bookings/{id}", methods=["GET"])
@app.api_route("/payments", methods=["GET", "POST"])
async def booking_routes(request: Request):
    return await forward_request(request, BOOKING_SERVICE_URL)

# Ticket Review Routes
@app.api_route("/tickets", methods=["GET"])
@app.api_route("/tickets/{id}", methods=["GET"])
@app.api_route("/reviews", methods=["POST"])
@app.api_route("/reviews/{event_id}", methods=["GET"])
@app.api_route("/checkin/{ticket_code}", methods=["POST"])
async def ticket_routes(request: Request):
    return await forward_request(request, TICKET_SERVICE_URL)
