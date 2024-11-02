from core.provider import (GoogleProviderSettings, Provider,
                           YandexProviderSettings)
from socials.exception import ProviderException
from socials.iprovider import IOAuthProvider
from socials.providers import GoogleOAuthProvider, YandexOAuthProvider


def get_provider(provider_name: str) -> IOAuthProvider:
    if provider_name == Provider.YANDEX:
        return YandexOAuthProvider(settings=YandexProviderSettings())
    elif provider_name == Provider.GOOGLE:
        return GoogleOAuthProvider(settings=GoogleProviderSettings())

    raise ProviderException(message="This provider is currently not supported")
