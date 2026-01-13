import csv
import io
from fastapi import BackgroundTasks

from app.iothub_http import create_device


def normalize_headers(fieldnames: list[str] | None) -> list[str]:
    if not fieldnames:
        return []
    return [h.strip().replace("\ufeff", "") for h in fieldnames]


def parse_csv_devices(csv_text: str) -> list[tuple[str, str | None]]:
    csv_file = io.StringIO(csv_text)
    reader = csv.DictReader(csv_file)

    # FIX: normalize headers (BOM / spaces)
    reader.fieldnames = normalize_headers(reader.fieldnames)

    devices: list[tuple[str, str | None]] = []

    for row in reader:
        pod_id = (row.get("DeviceId") or "").strip()
        status = (row.get("Status") or "").strip() or None

        if not pod_id:
            continue

        devices.append((pod_id, status))

    return devices


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
