from http.client import HTTPException
from fastapi import BackgroundTasks, UploadFile
from fastapi.params import File
import httpx

from app.pod_map import POD_DEVICE_MAP
from app.schemas import GoogleSheetRequest
from app.services.csv_parser import parse_csv_devices
from app.services.iothub.iothub_http import delete_devices, get_identity_device, send_c2d_message
from app.utils.device_queue import delete_devices_bulk, enqueue_devices, fetch_devices_info

# Control pod service
async def open_pod_service(pod_id: int, bg: BackgroundTasks):
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
    
    return device_id

# Create pod service
async def create_pod_devices_from_csv_service(
    file: UploadFile = File(...),
    bg: BackgroundTasks = BackgroundTasks()):
    
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

async def create_pod_devices_from_google_sheet_service(
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
    
async def create_pod_device_service(
    pod_id: str,
    bg: BackgroundTasks,
):
    created, _ = enqueue_devices([(pod_id, None)], bg)

    return {
        "status": "device creation initiated",
        "pod_id": created[0] if created else None,
    }
    
# Get pod service
async def get_devices_from_csv_service(
    file: UploadFile = File(...),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    devices = parse_csv_devices(content.decode("utf-8"))

    pod_ids = list({pod_id for pod_id, _ in devices})

    result = await fetch_devices_info(pod_ids)

    return {
        "status": "success",
        "source": "csv",
        "total": len(pod_ids),
        **result,
    }

async def get_devices_from_google_sheet_service(
    payload: GoogleSheetRequest,
):
    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=True,
    ) as client:
        response = await client.get(str(payload.sheet_url))
        response.raise_for_status()

    devices = parse_csv_devices(response.text)
    pod_ids = list({pod_id for pod_id, _ in devices})

    result = await fetch_devices_info(pod_ids)

    return {
        "status": "success",
        "source": "google_sheet",
        "total": len(pod_ids),
        **result,
    }
    
async def get_device_by_pod_id_service(
    pod_id: str,
):
    device_info = await get_identity_device(pod_id)

    if device_info is None:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "status": "success",
        "device_info": device_info,
    }
    
# Delete pod service
async def delete_devices_from_csv_service(
    file: UploadFile = File(...),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    devices = parse_csv_devices(content.decode("utf-8"))

    pod_ids = list({pod_id for pod_id, _ in devices})
    result = await delete_devices_bulk(pod_ids)

    return {
        "status": "success",
        "source": "csv",
        "total": len(pod_ids),
        **result,
    }
    
async def delete_devices_from_google_sheet_service(
    payload: GoogleSheetRequest,
):
    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=True,
    ) as client:
        response = await client.get(str(payload.sheet_url))
        response.raise_for_status()

    devices = parse_csv_devices(response.text)
    pod_ids = list({pod_id for pod_id, _ in devices})

    result = await delete_devices_bulk(pod_ids)

    return {
        "status": "success",
        "source": "google_sheet",
        "total": len(pod_ids),
        **result,
    }
    
async def delete_device_by_pod_id_service(
    pod_id: str,
):
    ok = await delete_devices(pod_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "status": "success",
        "deleted": pod_id,
    }