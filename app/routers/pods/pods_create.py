    
from fastapi import APIRouter, BackgroundTasks, UploadFile, File

from app.schemas.google_sheet import GoogleSheetRequest
from app.services.pods.pods_service import create_pod_device_service, create_pod_devices_from_csv_service, create_pod_devices_from_google_sheet_service

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