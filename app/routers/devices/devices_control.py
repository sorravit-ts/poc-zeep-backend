from fastapi import APIRouter, BackgroundTasks

from app.services.pods.devices_service import open_pod_service


router = APIRouter(prefix="/pods", tags=["devices:control"])

@router.post("/{pod_id}/open")
async def open_pod(pod_id: int, bg: BackgroundTasks):
    device_id = await open_pod_service(pod_id, bg)
    
    return {
        "status": "accepted",
        "pod_id": pod_id,
        "device_id": device_id,
    }