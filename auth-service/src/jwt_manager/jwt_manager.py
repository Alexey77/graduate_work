from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import InvalidHeaderError, JWTDecodeError
from core.config import JWTSettings
from core.logger import get_logger
from jwt.exceptions import DecodeError
from jwt_manager.exception import JWTException
from jwt_manager.ijwt import IAsyncJWTManager

logger = get_logger(__name__)


class JWTManager(IAsyncJWTManager):
    def __init__(self, settings: JWTSettings):
        self._settings = settings
        self._auth_jwt = AuthJWT()
        logger.info("JWTManager initialized with settings")

    @staticmethod
    @AuthJWT.load_config
    def get_config():
        return JWTSettings()

    async def decode_token(self, token: str) -> dict:
        try:
            return await self._auth_jwt.get_raw_jwt(token)
        except (InvalidHeaderError, JWTDecodeError):
            raise JWTException(message="Invalid token")

    async def create_access_token(self, subject: str, role: dict, **kwargs) -> str:
        return await self._auth_jwt.create_access_token(
            subject=subject, user_claims=role
        )

    async def create_refresh_token(self, subject: str, role: dict, **kwargs) -> str:
        return await self._auth_jwt.create_refresh_token(
            subject=subject, user_claims=role
        )

    async def create_tokens(
        self, subject: str, role: dict, **kwargs
    ) -> tuple[str, str]:
        return (
            await self.create_access_token(subject=subject, role=role),
            await self.create_refresh_token(subject=subject, role=role),
        )

    async def validate_access_token(self, access_token: str, **kwargs) -> bool:
        try:
            token = await self.decode_token(token=access_token)
            return token.get("type") == "access"
        except (InvalidHeaderError, JWTDecodeError):
            return False

    async def get_login_from_access_token(self, token: str) -> str:
        try:
            decoded_token = await self.decode_token(token)
            if decoded_token.get("type") == "access":
                return decoded_token.get("sub")
            raise JWTException(message="Access token is invalid or has expired.")
        except DecodeError:
            raise JWTException(message="Invalid or expired token")

    async def refresh_tokens(
        self, refresh_token: str, role: dict[str, list[str]], **kwargs
    ) -> tuple[str, str]:
        decoded_token = await self.decode_token(token=refresh_token)
        return (
            await self.create_access_token(subject=decoded_token["sub"], role=role),
            await self.create_refresh_token(subject=decoded_token["sub"], role=role),
        )

    async def get_roles_from_token(self, token: str) -> list[str]:
        decoded_token = await self.decode_token(token)
        return decoded_token.get("role", [])
