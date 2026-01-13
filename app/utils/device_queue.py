import csv
import io
from fastapi import BackgroundTasks

from app.services.iothub.iothub_http import create_device, delete_devices, get_identity_device


def enqueue_devices(
    devices: list[tuple[str, str | None]],
    bg: BackgroundTasks,
):
    seen: set[str] = set()
    created: list[str] = []
    duplicated: list[str] = []

    for pod_id, status in devices:
        if pod_id in seen:
            duplicated.append(pod_id)
            continue

        seen.add(pod_id)
        bg.add_task(create_device, pod_id, status)
        created.append(pod_id)

    return created, duplicated


async def fetch_devices_info(
    pod_ids: list[str],
) -> dict:
    found = {}
    not_found = []
    errors = {}

    for pod_id in pod_ids:
        try:
            device = await get_identity_device(pod_id)
            if device is None:
                not_found.append(pod_id)
            else:
                found[pod_id] = device
        except Exception as e:
            errors[pod_id] = str(e)

    return {
        "found": found,
        "not_found": not_found,
        "errors": errors,
    }

async def delete_devices_bulk(
    pod_ids: list[str],
) -> dict:
    deleted = []
    not_found = []
    errors = {}

    for pod_id in pod_ids:
        try:
            ok = await delete_devices(pod_id)
            if ok:
                deleted.append(pod_id)
            else:
                not_found.append(pod_id)
        except Exception as e:
            errors[pod_id] = str(e)

    return {
        "deleted": deleted,
        "not_found": not_found,
        "errors": errors,
    }
