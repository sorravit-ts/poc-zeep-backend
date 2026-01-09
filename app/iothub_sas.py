import time
import base64
import hmac
import hashlib
import urllib.parse

from .config import (
    IOTHUB_NAME,
    IOTHUB_POLICY_KEY,
    IOTHUB_POLICY_NAME,
)

_cached_sas: str | None = None
_cached_expiry: int = 0


def generate_sas_token(
    resource_uri: str,
    key: str,
    policy_name: str,
    expiry_seconds: int = 120,
) -> str:
    expiry = int(time.time()) + expiry_seconds
    encoded_uri = urllib.parse.quote_plus(resource_uri)

    to_sign = f"{encoded_uri}\n{expiry}".encode("utf-8")

    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(key),
            to_sign,
            hashlib.sha256,
        ).digest()
    )

    encoded_sig = urllib.parse.quote_plus(signature)

    return (
        "SharedAccessSignature "
        f"sr={encoded_uri}"
        f"&sig={encoded_sig}"
        f"&se={expiry}"
        f"&skn={policy_name}"
    )


def get_cached_sas_token() -> str:
    global _cached_sas, _cached_expiry

    now = int(time.time())

    if _cached_sas and now < _cached_expiry - 60:
        return _cached_sas

    expiry_seconds = 3600
    _cached_expiry = now + expiry_seconds

    _cached_sas = generate_sas_token(
        resource_uri=IOTHUB_NAME,
        key=IOTHUB_POLICY_KEY,
        policy_name=IOTHUB_POLICY_NAME,
        expiry_seconds=expiry_seconds,
    )

    return _cached_sas
