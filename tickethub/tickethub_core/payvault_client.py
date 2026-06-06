"""HTTP client for communicating with the PayVault microservice."""

import requests

PAYVAULT_BASE_URL = "http://localhost:5002/api"
TIMEOUT = 10  # seconds


class PayVaultClient:
    """Thin wrapper around PayVault REST endpoints."""

    @staticmethod
    def create_transaction(booking_id: int, amount: float, currency: str = "USD"):
        """Create a new pending transaction and return the response dict."""
        try:
            resp = requests.post(
                f"{PAYVAULT_BASE_URL}/transactions",
                json={
                    "booking_id": booking_id,
                    "amount": amount,
                    "currency": currency,
                },
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            return {"error": str(exc)}

    @staticmethod
    def confirm_payment(transaction_id: int):
        """Confirm a pending transaction."""
        try:
            resp = requests.post(
                f"{PAYVAULT_BASE_URL}/transactions/{transaction_id}/confirm",
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            return {"error": str(exc)}

    @staticmethod
    def fail_payment(transaction_id: int):
        """Mark a transaction as failed."""
        try:
            resp = requests.post(
                f"{PAYVAULT_BASE_URL}/transactions/{transaction_id}/fail",
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            return {"error": str(exc)}

    @staticmethod
    def refund_payment(transaction_id: int):
        """Issue a refund for a confirmed transaction."""
        try:
            resp = requests.post(
                f"{PAYVAULT_BASE_URL}/transactions/{transaction_id}/refund",
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            return {"error": str(exc)}

    @staticmethod
    def get_transactions(booking_id: int):
        """Retrieve all transactions for a given booking."""
        try:
            resp = requests.get(
                f"{PAYVAULT_BASE_URL}/transactions/booking/{booking_id}",
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            return {"error": str(exc)}
