import streamlit as st
import requests
import os

st.set_page_config(page_title="Payment Page", page_icon="💳")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.title("💳 Payment Page")

booking_id = st.number_input("Enter Booking ID", min_value=1, step=1)
payment_method = st.selectbox("Payment Method", ["CREDIT_CARD", "DEBIT_CARD", "PAYPAL", "BANK_TRANSFER"])

if st.button("Check Booking Status"):
    try:
        response = requests.get(f"{GATEWAY_URL}/bookings/{booking_id}")
        if response.status_code == 200:
            booking = response.json()
            st.write(f"**Total Price:** ${booking['total_price']}")
            st.write(f"**Status:** {booking['booking_status']}")
        else:
            st.error("Booking not found.")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")

if st.button("Pay Now"):
    payload = {
        "booking_id": booking_id,
        "payment_method": payment_method
    }
    try:
        response = requests.post(f"{GATEWAY_URL}/payments", json=payload)
        if response.status_code == 200:
            payment = response.json()
            st.success("Payment successful! Tickets are being generated.")
            st.json(payment)
        else:
            st.error(f"Payment failed: {response.json().get('detail')}")
    except requests.exceptions.RequestException:
        st.error("Error connecting to services.")
