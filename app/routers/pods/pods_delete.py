from fastapi import APIRouter, File, UploadFile

from app.schemas.google_sheet import GoogleSheetRequest
from app.services.pods.pods_service import delete_device_by_pod_id_service, delete_devices_from_csv_service, delete_devices_from_google_sheet_service


router = APIRouter(prefix="/pods/device", tags=["pods:delete"])
@router.delete("/csv")
async def delete_devices_from_csv(
    file: UploadFile = File(...),
):
    return await delete_devices_from_csv_service(file)


@router.delete("/google-sheet")
async def delete_devices_from_google_sheet(
    payload: GoogleSheetRequest,
):
    return await delete_devices_from_google_sheet_service(payload)

@router.delete("/{pod_id}")
async def delete_device_by_pod_id(pod_id: str):
    return await delete_device_by_pod_id_service(pod_id)