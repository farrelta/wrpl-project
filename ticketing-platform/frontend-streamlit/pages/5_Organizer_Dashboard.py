import streamlit as st
import requests
import os
import pandas as pd

st.set_page_config(page_title="Organizer Dashboard", page_icon="📊", layout="wide")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("📊 Organizer Dashboard")

organizer_id = st.number_input("Enter Organizer ID", min_value=1, step=1)

if st.button("Load Dashboard"):
    try:
        # Fetch events for this organizer
        response = requests.get(f"{GATEWAY_URL}/events")
        if response.status_code == 200:
            all_events = response.json()
            org_events = [e for e in all_events if e['organizer_id'] == organizer_id]
            
            if org_events:
                total_events = len(org_events)
                total_tickets_sold = sum([e['tickets_sold'] for e in org_events])
                total_revenue = sum([e['tickets_sold'] * e['price'] for e in org_events])
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Events", total_events)
                col2.metric("Tickets Sold", total_tickets_sold)
                col3.metric("Estimated Revenue", f"${total_revenue:,.2f}")
                
                st.subheader("Your Events")
                df = pd.DataFrame(org_events)
                st.dataframe(df[['event_id', 'event_name', 'category', 'event_date', 'price', 'quota', 'tickets_sold', 'status']])
            else:
                st.info("No events found for this organizer.")
        else:
            st.error("Could not fetch events.")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")
