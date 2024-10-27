from datetime import UTC, datetime


def get_current_time() -> datetime:
    return datetime.now(UTC)
