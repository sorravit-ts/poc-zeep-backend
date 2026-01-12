from fastapi import FastAPI, HTTPException, BackgroundTasks

from .pod_map import POD_DEVICE_MAP
from .schemas import OpenDoorCommand
from .iothub_http import send_c2d_message

app = FastAPI()


@app.post("/pods/{pod_id}/open")
async def open_pod(pod_id: int, bg: BackgroundTasks):
    # Map pod_id to device_id * รอ confirm pattern from IoT team ก่อน *
    device_id = POD_DEVICE_MAP.get(pod_id)

    if not device_id:
        raise HTTPException(status_code=404, detail="Pod not found")

    command = OpenDoorCommand()

    # 🔥 fire-and-forget
    bg.add_task(
        send_c2d_message,
        device_id,
        command.model_dump(),
    )

    # await send_c2d_message(device_id=device_id, payload=command.model_dump())

    return {
        "status": "accepted",
        "pod_id": pod_id,
        "device_id": device_id,
    }
