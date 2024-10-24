from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import UUID4, BaseModel, Field


# Request
class RequestAsk(BaseModel):
    dialogue: UUID4 | None = None
    content: Annotated[str, Field(min_length=1, max_length=4096)]

class RequestReply(BaseModel):
    id_ask: UUID4



# Response

class ResponseCreatedAsk(BaseModel):
    id_ask: UUID4


class ResponseCreatedUnauthorizedAsk(ResponseCreatedAsk):
    id_ask: UUID4 = UUID("77777777-7777-4777-8777-777777777777")


class Role(str, Enum):
    user = "user"
    assistant = "assistant"


class MessageModel(BaseModel):
    role: Role
    content: Annotated[str, Field(min_length=1, max_length=4096)]


class ReplyResponseModel(BaseModel):
    messages: list[MessageModel]


class ResponseMessage(BaseModel):
    message: str
