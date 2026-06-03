import streamlit as st
import requests
import os

st.set_page_config(page_title="My Tickets", page_icon="🎫")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("🎫 My Tickets")

attendee_id = st.number_input("Enter Attendee ID", min_value=1, step=1)

if st.button("View Tickets"):
    try:
        response = requests.get(f"{GATEWAY_URL}/tickets", params={"attendee_id": attendee_id})
        if response.status_code == 200:
            tickets = response.json()
            if not tickets:
                st.info("You don't have any tickets yet.")
            else:
                for t in tickets:
                    with st.container():
                        st.markdown(f"### Ticket: {t['ticket_code']}")
                        st.write(f"**Event ID:** {t['event_id']}")
                        st.write(f"**Seat:** {t['seat_number']}")
                        st.write(f"**Status:** {t['status']}")
                        st.divider()
        else:
            st.error("Could not fetch tickets.")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")

st.markdown("---")
st.subheader("Check-in Ticket (Scanner Simulator)")
ticket_code = st.text_input("Enter Ticket Code")
if st.button("Check In"):
    try:
        res = requests.post(f"{GATEWAY_URL}/checkin/{ticket_code}")
        if res.status_code == 200:
            st.success("Ticket checked in successfully!")
        else:
            st.error(f"Check-in failed: {res.json().get('detail')}")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")
