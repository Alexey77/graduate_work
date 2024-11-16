from datetime import datetime

from dialog_manager.models import DialogRoles
from dialog_manager.utilities import get_hash


def get_message_user(content: str, id_msg: str, created_at: datetime, **kwargs) -> dict[str, str | datetime]:
    return {
        "id": id_msg,
        "checksum": get_hash(content=content),
        "role": DialogRoles.user,
        "content": content,
        "created_at": created_at
    }
