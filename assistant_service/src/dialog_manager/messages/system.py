from dialog_manager.models import DialogRoles
from dialog_manager.utilities import get_hash


def get_system_message(**kwargs) -> dict[str, str]:
    content = """
        Ты AI ассистент в онлайн кинотеатре.
    """

    return {
        "id": get_hash(content=content),
        "role": DialogRoles.system,
        "content": content
    }
