from core.config import UserRole
from jwt_manager import IAsyncJWTManager
from services.exception import AccessException
from services.interface.iaccess import IAsyncAccessService


class AccessService(IAsyncAccessService):
    def __init__(self, jwt: IAsyncJWTManager):
        self._jwt = jwt

    async def verify_admin_access(self, access_token: str) -> None:
        if not await self._jwt.validate_access_token(access_token=access_token):
            raise AccessException(message="The token is invalid")
        roles = await self._jwt.get_roles_from_token(token=access_token)
        if UserRole.ADMINISTRATOR not in roles:
            msg = "Access Denied: Your account does not have sufficient permissions to perform this action."
            raise AccessException(message=msg)
