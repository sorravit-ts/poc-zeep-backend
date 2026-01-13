from fastapi import APIRouter, File, UploadFile

from app.schemas import GoogleSheetRequest
from app.services.pods.pods_service import get_device_by_pod_id_service, get_devices_from_csv_service, get_devices_from_google_sheet_service


router = APIRouter(prefix="/pods/device", tags=["pods:get"])

@router.get("/csv")
async def get_devices_from_csv(
    file: UploadFile = File(...),
):
    return await get_devices_from_csv_service(file)
    

@router.get("/google-sheet")
async def get_devices_from_google_sheet(
    payload: GoogleSheetRequest,
):
    return await get_devices_from_google_sheet_service(payload)

@router.get("/{pod_id}")
async def get_device_info(pod_id: str):
    return await get_device_by_pod_id_service(pod_id)