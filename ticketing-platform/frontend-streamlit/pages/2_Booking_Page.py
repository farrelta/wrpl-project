import streamlit as st
import requests
import os

st.set_page_config(page_title="Booking Page", page_icon="🎟️")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("🎟️ Booking Page")

attendee_id = st.number_input("Your Attendee ID", min_value=1, step=1)
event_id = st.number_input("Event ID to Book", min_value=1, step=1)
quantity = st.number_input("Quantity", min_value=1, step=1)

if st.button("Create Booking"):
    payload = {
        "attendee_id": attendee_id,
        "event_id": event_id,
        "quantity": quantity
    }
    
    try:
        response = requests.post(f"{GATEWAY_URL}/bookings", json=payload)
        if response.status_code == 200:
            booking = response.json()
            st.success("Booking created successfully!")
            st.json(booking)
            st.info("Please proceed to the Payment Page to complete your booking.")
        else:
            st.error(f"Failed to create booking: {response.json().get('detail')}")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")
