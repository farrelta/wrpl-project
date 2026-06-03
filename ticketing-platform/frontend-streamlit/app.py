import streamlit as st
import requests
import os

st.set_page_config(page_title="Multi-Company Ticketing", page_icon="🎫", layout="wide")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("🎫 Multi-Company Ticketing Platform")
st.subheader("Browse and Discover Events")

# Fetch all events
try:
    response = requests.get(f"{GATEWAY_URL}/events")
    events = response.json() if response.status_code == 200 else []
except requests.exceptions.RequestException:
    st.error("Could not connect to the backend services. Is the gateway running?")
    events = []

if events:
    # Categories for filter
    categories = list(set([e['category'] for e in events]))
    categories.insert(0, "All")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Filter by Category", categories)
    
    filtered_events = events
    if selected_category != "All":
        filtered_events = [e for e in events if e['category'] == selected_category]
        
    st.write(f"Showing {len(filtered_events)} events:")
    
    for event in filtered_events:
        with st.container():
            st.markdown(f"### {event['event_name']}")
            st.write(f"**Category:** {event['category']} | **Date:** {event['event_date']} | **Price:** ${event['price']}")
            st.write(f"**Quota:** {event['quota']} | **Sold:** {event['tickets_sold']}")
            st.divider()
else:
    st.info("No events found. Check back later!")

st.sidebar.markdown("### Navigation")
st.sidebar.info("Use the pages above to navigate through the platform.")
