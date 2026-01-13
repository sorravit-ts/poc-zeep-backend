import time
import base64
import hmac
import hashlib
import urllib.parse

from app.core.config import (
    IOTHUB_NAME,
    IOTHUB_POLICY_KEY,
    IOTHUB_POLICY_NAME,
)


# -------------------------
# ตัวแปรสำหรับ cache SAS Token
# -------------------------

_cached_sas: str | None = None   # เก็บ SAS Token ล่าสุด
_cached_expiry: int = 0          # เวลา expiry (epoch time)


def generate_sas_token(
    resource_uri: str,
    key: str,
    policy_name: str,
    expiry_seconds: int = 120,
) -> str:
    """
    สร้าง Shared Access Signature (SAS Token)
    ใช้สำหรับ authenticate กับ Azure IoT Hub
    """
    # เวลาหมดอายุของ token (epoch time)
    expiry = int(time.time()) + expiry_seconds

    # encode resource uri ให้ปลอดภัยสำหรับ URL
    encoded_uri = urllib.parse.quote_plus(resource_uri)

    # string ที่ต้องใช้ในการ sign ตามรูปแบบของ Azure
    # รูปแบบคือ: "<resource_uri>\n<expiry>"
    to_sign = f"{encoded_uri}\n{expiry}".encode("utf-8")

    # สร้าง HMAC-SHA256 signature
    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(key),  # decode key จาก base64 ก่อน
            to_sign,
            hashlib.sha256,
        ).digest()
    )

    # encode signature ให้อยู่ในรูป URL-safe
    encoded_sig = urllib.parse.quote_plus(signature)

    return (
        "SharedAccessSignature "
        f"sr={encoded_uri}"
        f"&sig={encoded_sig}"
        f"&se={expiry}"
        f"&skn={policy_name}"
    )


def get_cached_sas_token() -> str:
    """
    คืนค่า SAS Token โดยใช้ cache
    - ถ้า token เดิมยังไม่หมดอายุ → ใช้ซ้ำ
    - ถ้าใกล้หมดอายุหรือหมดแล้ว → สร้างใหม่
    """
    global _cached_sas, _cached_expiry

    now = int(time.time())

    # ถ้ามี token อยู่แล้ว และยังไม่ใกล้หมดอายุ (เหลือมากกว่า 60 วินาที)
    if _cached_sas and now < _cached_expiry - 60:
        return _cached_sas

    expiry_seconds = 3600
    _cached_expiry = now + expiry_seconds

    # สร้าง SAS Token ใหม่ และเก็บลง cache
    _cached_sas = generate_sas_token(
        resource_uri=IOTHUB_NAME,
        key=IOTHUB_POLICY_KEY,
        policy_name=IOTHUB_POLICY_NAME,
        expiry_seconds=expiry_seconds,
    )

    return _cached_sas
