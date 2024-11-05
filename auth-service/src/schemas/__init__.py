from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr

jwt_token = Field(
    pattern=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$", min_length=16
)


class ResponseAuthTokens(BaseModel):
    access_token: str = jwt_token
    refresh_token: str = jwt_token

    model_config = ConfigDict(regex_engine="python-re")


class ResponseMessage(BaseModel):
    message: str


class UserHistoryItem(BaseModel):
    user_agent: str
    time: datetime


class ResponseUserHistory(BaseModel):
    history: list[UserHistoryItem]


class UserPassUpdate(BaseModel):
    login: EmailStr = Field(..., alias="email")
    old_password: constr(min_length=1)
    new_password: constr(min_length=1)


class UserCredentials(BaseModel):
    login: EmailStr = Field(..., alias="email")
    password: constr(min_length=1)


class UserRegistration(UserCredentials, BaseModel):
    first_name: str = ""
    last_name: str = ""


class UserRole(BaseModel):
    user_name: constr(min_length=1)
    role_name: constr(min_length=1, max_length=256)


class Role(BaseModel):
    name: str
    description: str | None

    class Config:
        from_attributes = True


class ResponseUserPermissions(BaseModel):
    login: str
    permissions: list[str]
