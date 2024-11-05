from functools import lru_cache

from models.user_provider import UserProvider
from pydantic import ValidationError
from services.interface.iprovider import IProviderService
from socials import get_provider
from socials.exception import ProviderException
from socials.iprovider import IOAuthProvider
from starlette.requests import Request

from .exception import SocialException


class ProviderService(IProviderService):
    @staticmethod
    def _get_provider(provider_name: str) -> IOAuthProvider:
        try:
            return get_provider(provider_name=provider_name)
        except ProviderException as e:
            raise SocialException(message=e.message)

    def get_authorization_url(self, provider_name: str) -> str:
        provider = self._get_provider(provider_name=provider_name)
        return provider.get_authorization_url()

    async def authorize(self, provider_name: str, request: Request) -> UserProvider:
        provider = self._get_provider(provider_name=provider_name)

        try:
            access_token = await provider.get_access_token(
                query_params=dict(request.query_params)
            )
            if access_token is None:
                raise SocialException(message="Authorization error")

            user_info = await provider.get_user_info(access_token=access_token)
        except ProviderException as e:
            raise SocialException(message=e.message)

        try:
            return UserProvider.from_provider(
                data=user_info, provider_name=provider_name
            )
        except ValidationError as e:
            raise SocialException(message=e.message)


@lru_cache
def get_provider_service() -> IProviderService:
    return ProviderService()
