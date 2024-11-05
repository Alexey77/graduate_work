import random
import string
from typing import Self

from core.provider import Provider
from pydantic import BaseModel, EmailStr, constr


def generate_random_password(length: int = 32) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.SystemRandom().choice(characters) for _ in range(length))


class UserProvider(BaseModel):
    id_social: constr(min_length=1)
    login: EmailStr
    password: constr(min_length=1)
    provider: Provider

    @classmethod
    def from_yandex(cls, data: dict):
        return cls(
            id_social=data["id"],
            login=data["default_email"],
            password=generate_random_password(),
            provider=Provider.YANDEX,
        )

    @classmethod
    def from_google(cls, data: dict):
        return cls(
            id_social=data["id"],
            login=data["email"],
            password=generate_random_password(),
            provider=Provider.GOOGLE,
        )

    @classmethod
    def from_provider(cls, data: dict, provider_name: str) -> Self:
        if provider_name == Provider.YANDEX:
            return UserProvider.from_yandex(data=data)
        elif provider_name == Provider.GOOGLE:
            return UserProvider.from_google(data=data)
        else:
            err_msg = f"Unsupported provider: {provider_name}"
            raise ValueError(err_msg)
