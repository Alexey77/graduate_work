import http
from functools import lru_cache

import aiohttp
import jwt
from fastapi.exceptions import HTTPException

from core.config import AuthServiceSettings, auth_service_settings
from core.logger import get_logger
from schemes import User

logger = get_logger(__name__)


class AuthService:
    def __init__(self, config: AuthServiceSettings) -> None:
        self._base_url = config.url
        self._secret_key = config.secret_key
        self._algorithm = config.algorithm

    def _decode_token(self, token: str) -> User:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return User(email=payload.get("sub"), roles=payload.get("role"))
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED, detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED, detail="Invalid token"
            )

    async def validate_access_token(self, access_token: str) -> None:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self._base_url}/auth/token/validate",
                headers={"Authorization": f"Bearer {access_token}"},
            ) as response,
        ):
            response.raise_for_status()
            return await response.json()

    async def get_login_from_access_token(self, access_token: str) -> str | None:
        return "morty.smith@earth.dimensionC137"

    async def get_current_user(
        self, access_token: str, external_validation: bool = False
    ) -> User:
        # сначала проверяем что токен валидный и не истек, чтобы не делать лишний запрос на внешний сервис если токен невалидный
        user = self._decode_token(access_token)
        if external_validation:
            try:
                await self.validate_access_token(access_token)
            except aiohttp.ClientResponseError as e:
                logger.warning("Failed to validate access token: %s", e)
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED, detail="Invalid token"
                )
        return user

    async def get_current_user_permissions(self, access_token: str) -> dict:
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                f"{self._base_url}/auth/permissions",
                headers={"Authorization": f"Bearer {access_token}"},
            ) as response,
        ):
            response.raise_for_status()
            return await response.json()


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(auth_service_settings)
