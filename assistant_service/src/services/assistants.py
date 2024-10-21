from functools import lru_cache

from pydantic import UUID4
from schemes import Role

# from dependencies import get_db


class AssistantsService:
    def __init__(self,
                 # db
                 ) -> None:
        pass
        # self._db = db

    async def create_or_update_session(self, content: str, session: UUID4 | None, user: str) -> UUID4:
        pass

    async def unauthorized_reply(self) -> list[dict]:
        message = "Чтобы продолжить диалог Вам нужно авторизоваться!"

        return [

            {"role": Role.assistant.value, "content": message}
        ]


@lru_cache
def get_assistants_service(
        # db=Depends(get_db)
) -> AssistantsService:
    return AssistantsService(
        # db
    )
