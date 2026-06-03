import streamlit as st
import requests
import os

st.set_page_config(page_title="Review Page", page_icon="⭐")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("⭐ Event Reviews")

tab1, tab2 = st.tabs(["Submit a Review", "View Reviews"])

with tab1:
    st.subheader("Submit Review")
    attendee_id = st.number_input("Attendee ID (Reviewer)", min_value=1, step=1)
    event_id_submit = st.number_input("Event ID to Review", min_value=1, step=1)
    rating = st.slider("Rating", 1.0, 5.0, 5.0, 0.5)
    comment = st.text_area("Comment")
    
    if st.button("Submit Review"):
        payload = {
            "attendee_id": attendee_id,
            "event_id": event_id_submit,
            "rating": rating,
            "comment": comment
        }
        try:
            res = requests.post(f"{GATEWAY_URL}/reviews", json=payload)
            if res.status_code == 200:
                st.success("Review submitted successfully!")
            else:
                st.error(f"Failed to submit: {res.json().get('detail')}")
        except requests.exceptions.RequestException:
            st.error("Error connecting to services.")

with tab2:
    st.subheader("View Event Reviews")
    event_id_view = st.number_input("Enter Event ID to see reviews", min_value=1, step=1)
    if st.button("Load Reviews"):
        try:
            res = requests.get(f"{GATEWAY_URL}/reviews/{event_id_view}")
            if res.status_code == 200:
                reviews = res.json()
                if not reviews:
                    st.info("No reviews yet.")
                else:
                    for r in reviews:
                        st.markdown(f"**Rating:** {r['rating']} / 5")
                        st.write(r['comment'])
                        st.caption(f"Attendee ID: {r['attendee_id']} | Date: {r['created_at']}")
                        st.divider()
            else:
                st.error("Failed to load reviews.")
        except requests.exceptions.RequestException:
            st.error("Error connecting to services.")
