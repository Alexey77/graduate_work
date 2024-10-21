from functools import lru_cache

# from dependencies import get_db


class AuthService:
    def __init__(self,
                 # cache
                 ) -> None:
        pass
        # self._db = db

    async def validate_access_token(self, access_token: str, **kwargs) -> bool:
        return True

    async def get_login_from_access_token(self, access_token: str, **kwargs) -> str | None:
        return "morty.smith@earth.dimensionC137"


@lru_cache
def get_auth_service(
        # cache: IAsyncCache = Depends(get_cache),
) -> AuthService:
    return AuthService(
        # db
    )
