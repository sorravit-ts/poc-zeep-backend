def normalize_headers(fieldnames: list[str] | None) -> list[str]:
    if not fieldnames:
        return []
    return [h.strip().replace("\ufeff", "") for h in fieldnames]


def normalize_device_status(status: str | None) -> str:
    if not status:
        return "enabled"

    status = status.strip().lower()

    if status in {"enable", "enabled", "true", "1"}:
        return "enabled"

    if status in {"disable", "disabled", "false", "0"}:
        return "disabled"

    # default fallback
    return "enabled"
