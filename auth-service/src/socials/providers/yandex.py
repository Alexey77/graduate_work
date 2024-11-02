from urllib.parse import urlencode, urlsplit, urlunparse

from networking.aiohttp import AiohttpNetworkClient
from networking.httpx import NetworkException

from ..exception import ProviderException
from ..iprovider import IOAuthProvider


class YandexOAuthProvider(AiohttpNetworkClient, IOAuthProvider):
    TOKEN_URL = "https://oauth.yandex.ru/token"
    USER_INFO_URL = "https://login.yandex.ru/info"
    AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"

    RESPONSE_TYPE = "code"

    def get_authorization_url(self) -> str:
        query_params = {
            "response_type": self.RESPONSE_TYPE,
            "client_id": self._settings.CLIENT_ID
        }
        url_parts = urlsplit(self.AUTHORIZE_URL)

        return urlunparse((url_parts.scheme, url_parts.netloc, url_parts.path, '',
                           urlencode(query_params), ''))

    async def get_access_token(self, query_params: dict) -> str:

        try:
            data = {
                "code": query_params[self.RESPONSE_TYPE],
                "grant_type": "authorization_code",
                "client_id": self._settings.CLIENT_ID,
                "client_secret": self._settings.CLIENT_SECRET,
            }
        except KeyError as e:
            raise ProviderException(message=f"Missing required key: {e}")

        headers_string = self.encode_base64(f"{self._settings.CLIENT_ID}:{self._settings.CLIENT_SECRET}")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {headers_string}"
        }
        try:
            response = await self.post(url=self.TOKEN_URL, data=data, headers=headers)
            return response.get("access_token")
        except NetworkException as e:
            raise ProviderException(message=e.message)

    async def get_user_info(self, access_token: str) -> dict:
        params = {"format": "json"}
        headers = {"Authorization": f"OAuth {access_token}"}

        return await self.post(url=self.USER_INFO_URL, data=params, headers=headers)
