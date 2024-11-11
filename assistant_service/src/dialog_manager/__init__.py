from functools import lru_cache

from fastapi import Depends
from pydantic import UUID4

from core.logger import get_logger
from database.mongodb.dialog import DialoguesMongoDB
from dependencies import get_db_dialogue
from dialog_manager.messages import get_message_user, get_system_message
from dialog_manager.models import DialogModel

logger = get_logger(__name__)


class DialogManager:

    def __init__(self, db) -> None:
        self._db: DialoguesMongoDB = db

    async def create_dialog(self, content: str, user: str) -> UUID4:
        new_dialog = DialogModel.new(user=user)

        system_message = get_system_message()
        new_dialog.messages.append(system_message)

        message_user = get_message_user(content=content,
                                        id_msg=str(new_dialog.id_last_ask),
                                        created_at=new_dialog.created_at)

        new_dialog.messages.append(message_user)

        await self._db.add_new_dialogue(dialog=new_dialog.to_mongodb())
        logger.info(f"Added a new dialog with _id:{new_dialog.id_dialog}")
        return new_dialog.id_last_ask


@lru_cache
def get_db_dialogue_manager(db: DialoguesMongoDB = Depends(get_db_dialogue)) -> DialogManager:
    return DialogManager(db)
