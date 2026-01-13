# # app/iothub_http.py
import json
import httpx

from app.core.config import IOTHUB_NAME
from app.services.iothub.iothub_sas import get_cached_sas_token
from app.utils.normalize import normalize_device_status


API_VERSION = "2021-04-12"

http_client = httpx.AsyncClient(
    timeout=5.0,
)


async def send_c2d_message(device_id: str, payload: dict) -> None:
    # Get SAS token
    sas_token = get_cached_sas_token()

    url = (
        f"https://{IOTHUB_NAME}"
        f"/devices/{device_id}/messages/deviceBound"
        f"?api-version={API_VERSION}"
    )

    # Send the C2D message
    response = await http_client.post(
        url,
        headers={
            "Authorization": sas_token,
            "Content-Type": "application/json",
        },
        content=json.dumps(payload),
    )

    response.raise_for_status()


async def create_device(
    pod_id: str,
    status: str | None = None,
) -> None:
    sas_token = get_cached_sas_token()

    url = (
        f"https://{IOTHUB_NAME}"
        f"/devices/{pod_id}"
        f"?api-version={API_VERSION}"
    )

    payload = {
        "deviceId": pod_id,
        "status": normalize_device_status(status),
        "authentication": {
            "type": "sas",
            "symmetricKey": {
                "primaryKey": "",
                "secondaryKey": ""
            }
        }
    }

    response = await http_client.put(
        url,
        headers={
            "Authorization": sas_token,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    response.raise_for_status()

async def get_identity_device(pod_id: str) -> dict | None:
    sas_token = get_cached_sas_token()

    url = (
        f"https://{IOTHUB_NAME}"
        f"/devices/{pod_id}"
        f"?api-version={API_VERSION}"
    )

    response = await http_client.get(
        url,
        headers={
            "Authorization": sas_token,
            "Content-Type": "application/json",
        },
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()

async def delete_devices(pod_id: str) -> None:
    sas_token = get_cached_sas_token()

    url = (
        f"https://{IOTHUB_NAME}"
        f"/devices/{pod_id}"
        f"?api-version={API_VERSION}"
    )

    response = await http_client.delete(
        url,
        headers={
            "Authorization": sas_token,
            "If-Match": "*",
            "Content-Type": "application/json",
        },
    )

    response.raise_for_status()
    return True