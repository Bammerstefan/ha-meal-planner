"""Ed25519-signed perpetual offline module licenses."""
import base64
import json
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .license_public_key import PUBLIC_KEY_B64

MODULES = {"shopping_pro": "Einkaufsliste PRO", "recipes_pro": "Rezeptbuch PRO", "family_pro": "Familienmodul"}

def verify_license(token, installation_id):
    try:
        payload_b64, signature_b64 = token.strip().split(".")
        def decode(s):
            return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
        payload_bytes, signature = decode(payload_b64), decode(signature_b64)
        Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBLIC_KEY_B64)).verify(signature, payload_bytes)
        data = json.loads(payload_bytes)
        if data.get("schema") != 1 or data.get("installation_id") != installation_id:
            raise ValueError("License is for a different installation")
        if not data.get("modules") or not isinstance(data["modules"], list) or any(m not in MODULES for m in data["modules"]):
            raise ValueError("Invalid modules")
        if not isinstance(data.get("license_id"), str) or not data["license_id"]:
            raise ValueError("Missing license ID")
        return data
    except Exception as exc:
        raise ValueError("Ungültiger Lizenzschlüssel oder andere Installation") from exc
