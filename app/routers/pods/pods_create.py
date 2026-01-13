    
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File

from app.schemas import GoogleSheetRequest
from app.services.csv_parser import parse_csv_devices
from app.services.pods.pods_service import create_pod_device_service, create_pod_devices_from_csv_service, create_pod_devices_from_google_sheet_service
from app.utils.device_queue import enqueue_devices

router = APIRouter(prefix="/pods/new-device", tags=["pods:create"])

@router.post("/csv")
async def create_pod_devices_from_csv(
    file: UploadFile = File(...),
    bg: BackgroundTasks = BackgroundTasks(),
):
    return await create_pod_devices_from_csv_service(file, bg)

@router.post("/google-sheet")
async def create_pod_devices_from_google_sheet(
    payload: GoogleSheetRequest,
    bg: BackgroundTasks,
):
    return await create_pod_devices_from_google_sheet_service(payload, bg)

@router.post("/{pod_id}")
async def create_pod_device(
    pod_id: str,
    bg: BackgroundTasks,
):
    return await create_pod_device_service(pod_id, bg)