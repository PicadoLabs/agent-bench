import pytest
import time
from auth_service import AuthService


def test_valid_token_verification():
    auth = AuthService("super-secret-key-12345")
    token = auth.generate_token({"user_id": 42, "role": "admin"})
    payload = auth.verify_token(token)
    assert payload is not None
    assert payload["user_id"] == 42
    assert payload["role"] == "admin"


def test_tampered_payload_rejected():
    auth = AuthService("super-secret-key-12345")
    token = auth.generate_token({"user_id": 42, "role": "user"})
    parts = token.split(".")
    # Tamper payload
    tampered_token = f"{parts[0]}.eyAidXNlcl9pZCI6IDQyLCAicm9sZSI6ICJhZG1pbiIgfQ.{parts[2]}"
    assert auth.verify_token(tampered_token) is None


def test_invalid_signature_rejected():
    auth1 = AuthService("key-one")
    auth2 = AuthService("key-two")
    token = auth1.generate_token({"user_id": 1})
    # auth2 has different secret, so verify must return None
    assert auth2.verify_token(token) is None


def test_none_algorithm_rejected():
    auth = AuthService("super-secret-key-12345")
    # Alg 'none' token
    fake_token = "eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJ1c2VyX2lkIjogOTksICJyb2xlIjogImFkbWluIn0."
    assert auth.verify_token(fake_token) is None


def test_expired_token_rejected():
    auth = AuthService("super-secret-key-12345")
    token = auth.generate_token({"user_id": 42}, expires_in_seconds=-10)
    assert auth.verify_token(token) is None


def test_malformed_token():
    auth = AuthService("super-secret-key-12345")
    assert auth.verify_token("invalid.token") is None
    assert auth.verify_token("not-a-token") is None
    assert auth.verify_token("") is None
