import streamlit as st
import requests
import os

st.set_page_config(page_title="Event Detail", page_icon="ℹ️")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("ℹ️ Event Detail")

event_id = st.number_input("Enter Event ID", min_value=1, step=1)

if st.button("Get Details"):
    try:
        response = requests.get(f"{GATEWAY_URL}/events/{event_id}")
        if response.status_code == 200:
            event = response.json()
            st.success(f"Details for: {event['event_name']}")
            
            st.write(f"**Date:** {event['event_date']}")
            st.write(f"**Time:** {event['start_time']} - {event['end_time']}")
            st.write(f"**Price:** ${event['price']}")
            
            # Remaining Quota
            remaining = event['quota'] - event['tickets_sold']
            st.write(f"**Remaining Quota:** {remaining}")
            
            # Venue Information
            v_response = requests.get(f"{GATEWAY_URL}/venues")
            if v_response.status_code == 200:
                venues = v_response.json()
                venue = next((v for v in venues if v['venue_id'] == event['venue_id']), None)
                if venue:
                    st.subheader("Venue Information")
                    st.write(f"**Name:** {venue['venue_name']}")
                    st.write(f"**Address:** {venue['address']}, {venue['city']}")
        else:
            st.error("Event not found.")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")
