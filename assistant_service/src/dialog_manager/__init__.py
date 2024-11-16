from datetime import datetime
from functools import lru_cache

from core.logger import get_logger
from database.mongodb.dialog import DialoguesMongoDB
from dependencies import get_db_dialogue
from dialog_manager.messages import get_message_user, get_system_message
from dialog_manager.models import DialogModel
from fastapi import Depends
from pydantic import UUID4

logger = get_logger(__name__)


class DialogManager:

    def __init__(self, db) -> None:
        self._db: DialoguesMongoDB = db

    async def create_dialog(self, user: str) -> UUID4:
        new_dialog = DialogModel.new(user=user)
        await self._db.add_new_dialogue(dialog=new_dialog.to_mongodb())
        logger.info(f"Added a new dialog with _id:{new_dialog.id_dialog}")
        return new_dialog.id_dialog

    async def save_dialog(self, dialog_id: UUID4, messages: list) -> None:
        dialog_data = await self._db.find_dialog_by_id(dialog_id)
        if not dialog_data:
            logger.error(f"Dialog with _id:{dialog_id} not found")
            return

        dialog = DialogModel(**dialog_data)
        dialog.update_at = datetime.utcnow()
        dialog.messages.extend([msg.dict() for msg in messages])
        await self._db.update_dialogue(dialog=dialog.to_mongodb())
        logger.info(f"Dialog with _id:{dialog.id_dialog} updated")


@lru_cache
def get_db_dialogue_manager(db: DialoguesMongoDB = Depends(get_db_dialogue)) -> DialogManager:
    return DialogManager(db)
