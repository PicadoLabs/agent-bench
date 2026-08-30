# auth_service.py - Authentication & Token Verification Service
import time
import base64
import json
import hmac
import hashlib
from typing import Optional, Dict, Any


class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def _base64_url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    def _base64_url_decode(self, data: str) -> bytes:
        rem = len(data) % 4
        if rem > 0:
            data += '=' * (4 - rem)
        return base64.urlsafe_b64decode(data.encode('utf-8'))

    def generate_token(self, payload: Dict[str, Any], expires_in_seconds: int = 3600) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        exp = int(time.time()) + expires_in_seconds
        full_payload = {**payload, "exp": exp}
        
        h_enc = self._base64_url_encode(json.dumps(header).encode('utf-8'))
        p_enc = self._base64_url_encode(json.dumps(full_payload).encode('utf-8'))
        signing_input = f"{h_enc}.{p_enc}"
        
        signature = hmac.new(self.secret_key.encode('utf-8'), signing_input.encode('utf-8'), hashlib.sha256).digest()
        s_enc = self._base64_url_encode(signature)
        return f"{signing_input}.{s_enc}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload if valid, or None if invalid/expired/tampered.
        """
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        h_enc, p_enc, s_enc = parts
        try:
            header = json.loads(self._base64_url_decode(h_enc).decode('utf-8'))
            payload = json.loads(self._base64_url_decode(p_enc).decode('utf-8'))
        except Exception:
            return None

        # BUG: Algorithm confusion vulnerability & broken signature check
        # Incorrectly accepts 'none' algorithm and does not verify signature properly
        if header.get("alg") == "none":
            return payload  # Vulnerability!

        # Broken signature validation logic:
        # BUG: It checks if len(s_enc) == 0 instead of computing and checking HMAC signature
        if len(s_enc) == 0:
            return None

        # BUG: Missing expiry check (exp)
        return payload
