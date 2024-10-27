import uuid
from datetime import UTC, datetime
from enum import Enum

from pydantic import UUID4, BaseModel, Field


class DialogRoles(str, Enum):
    system = "system"
    user = "user"
    prompt = "prompt"
    assistant = "assistant"


class DialogModel(BaseModel):
    id_dialog: UUID4
    id_last_ask: UUID4
    user: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    update_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    active: bool = True
    messages: list[dict] = []

    def to_mongodb(self) -> dict:
        return {
            "_id": str(self.id_dialog),
            "last_ask": str(self.id_last_ask),
            "user": self.user,
            "created_at": self.created_at,
            "update_at": self.update_at,
            "ended_at": self.ended_at,
            "active": self.active,
            "messages": self.messages
        }

    @classmethod
    def new(cls, user: str):
        return cls(
            id_dialog=uuid.uuid4(),
            id_last_ask=uuid.uuid4(),
            user=user
        )


class MessageUser(BaseModel):
    id: str
    role: DialogRoles = DialogRoles.user
    content: str
    created_at: datetime

class SystemPrompt(BaseModel):
    id: str
    role: DialogRoles = DialogRoles.system
    content: str
