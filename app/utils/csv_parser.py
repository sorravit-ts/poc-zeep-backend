
import csv
import io

from app.utils.normalize import normalize_headers

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
