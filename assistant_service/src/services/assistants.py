from functools import lru_cache
from typing import TYPE_CHECKING

from fastapi import Depends
from pydantic import UUID4

from dialog_manager import get_db_dialogue_manager
from schemes import Role

if TYPE_CHECKING:
    from dialog_manager import DialogManager


class AssistantsService:
    def __init__(self, dialog) -> None:
        self._dialog: DialogManager = dialog

    async def _create_dialogue(self, content: str, user: str) -> UUID4:
        return await self._dialog.create_dialog(content=content, user=user)

    async def _update_dialogue(
        self, ask: str, id_dialog: UUID4 | None, user: str
    ) -> UUID4:
        raise NotImplementedError

    async def create_or_update_dialogue(
        self, content: str, id_dialog: UUID4 | None, user: str
    ) -> UUID4:
        if id_dialog is None:
            return await self._create_dialogue(content=content, user=user)

        if isinstance(id_dialog, UUID4):
            return await self._update_dialogue(content, id_dialog, user)

        raise ValueError

    async def unauthorized_reply(self) -> list[dict]:
        message = "Чтобы продолжить диалог Вам нужно авторизоваться!"

        return [{"role": Role.assistant, "content": message}]


@lru_cache
def get_assistants_service(
    dialog=Depends(get_db_dialogue_manager),
) -> AssistantsService:
    return AssistantsService(dialog)
