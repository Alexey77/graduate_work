from core.config import JWTSettings

from .ijwt import IAsyncJWTManager
from .jwt_manager import JWTManager


def jwt_manager_factory(settings: JWTSettings, **kwargs) -> IAsyncJWTManager:
    return JWTManager(settings=settings)
