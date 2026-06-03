$attendee = @{
    full_name = "John Doe"
    email = "john@example.com"
    phone = "1234567890"
    city = "New York"
    birth_date = "1990-01-01"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/register-attendee" -Method Post -ContentType "application/json" -Body $attendee

$organizer = @{
    company_name = "Tech Events LLC"
    email = "contact@techevents.com"
    phone = "0987654321"
    city = "San Francisco"
    organizer_type = "Technology"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/register-organizer" -Method Post -ContentType "application/json" -Body $organizer

$venue = @{
    venue_name = "Moscone Center"
    city = "San Francisco"
    address = "747 Howard St"
    capacity = 5000
    venue_type = "Convention Center"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/venues" -Method Post -ContentType "application/json" -Body $venue

$event = @{
    organizer_id = 1
    venue_id = 1
    event_name = "Tech Conference 2026"
    category = "Technology"
    event_date = "2026-10-15"
    start_time = "09:00:00"
    end_time = "18:00:00"
    price = 199.99
    quota = 1000
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/events" -Method Post -ContentType "application/json" -Body $event

Write-Host "Database seeded successfully!"
