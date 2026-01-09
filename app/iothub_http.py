# # app/iothub_http.py
import json
import httpx

from .config import IOTHUB_NAME
from .iothub_sas import get_cached_sas_token

API_VERSION = "2021-04-12"

http_client = httpx.AsyncClient(
    timeout=5.0,
)


async def send_c2d_message(device_id: str, payload: dict) -> None:
    sas_token = get_cached_sas_token()

    url = (
        f"https://{IOTHUB_NAME}"
        f"/devices/{device_id}/messages/deviceBound"
        f"?api-version={API_VERSION}"
    )

    response = await http_client.post(
        url,
        headers={
            "Authorization": sas_token,
            "Content-Type": "application/json",
        },
        content=json.dumps(payload),
    )

    response.raise_for_status()


