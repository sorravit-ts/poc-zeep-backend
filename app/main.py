from xmlrpc import client
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile
import csv
import io

from fastapi.params import File
import httpx

from app.services.devices import enqueue_devices, parse_csv_devices


from .pod_map import POD_DEVICE_MAP
from .schemas import OpenDoorCommand, GoogleSheetRequest
from .iothub_http import create_device, send_c2d_message

app = FastAPI()


@app.post("/pods/{pod_id}/open")
async def open_pod(pod_id: int, bg: BackgroundTasks):
    # Map pod_id to device_id * รอ confirm pattern from IoT team ก่อน *
    device_id = POD_DEVICE_MAP.get(pod_id)

    if not device_id:
        raise HTTPException(status_code=404, detail="Pod not found")

    # command = OpenDoorCommand()

    payload = [
        {
            "type": "air",
            "action": "OPEN_AIR",
        },
        {
            "type": "door",
            "action": "OPEN_DOOR",
        },
    ]
    # 🔥 fire-and-forget
    bg.add_task(
        send_c2d_message,
        device_id,
        payload
    )

    # await send_c2d_message(device_id=device_id, payload=command.model_dump())

    return {
        "status": "accepted",
        "pod_id": pod_id,
        "device_id": device_id,
    }
    
@app.post("/pods/new-device/csv")
async def create_pod_devices_from_csv(
    file: UploadFile = File(...),
    bg: BackgroundTasks = BackgroundTasks(),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    devices = parse_csv_devices(content.decode("utf-8"))

    created, duplicated = enqueue_devices(devices, bg)

    return {
        "status": "device creation initiated",
        "source": "csv",
        "created": created,
        "duplicated": duplicated,
        "total": len(created),
    }

@app.post("/pods/new-device/google-sheet")
async def create_pod_devices_from_google_sheet(
    payload: GoogleSheetRequest,
    bg: BackgroundTasks,
):
    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=True,
    ) as client:
        response = await client.get(str(payload.sheet_url))
        response.raise_for_status()

    devices = parse_csv_devices(response.text)
    created, duplicated = enqueue_devices(devices, bg)

    return {
        "status": "device creation initiated",
        "source": "google_sheet",
        "created": created,
        "duplicated": duplicated,
        "total": len(created),
    }

@app.post("/pods/new-device/{pod_id}")
async def create_pod_device(
    pod_id: str,
    bg: BackgroundTasks,
):
    created, _ = enqueue_devices([(pod_id, None)], bg)

    return {
        "status": "device creation initiated",
        "pod_id": created[0] if created else None,
    }
