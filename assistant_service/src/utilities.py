from datetime import datetime, UTC


def get_current_time() -> datetime:
    return datetime.now(UTC)
