from urllib.parse import urlencode, urlsplit, urlunparse

from networking.aiohttp import AiohttpNetworkClient
from networking.httpx import NetworkException
from socials.exception import ProviderException
from socials.iprovider import IOAuthProvider


class GoogleOAuthProvider(AiohttpNetworkClient, IOAuthProvider):
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"

    RESPONSE_TYPE = "code"
    SCOPE = "https://www.googleapis.com/auth/userinfo.email"

    def get_authorization_url(self) -> str:
        query_params = {
            "response_type": self.RESPONSE_TYPE,
            "redirect_uri": self._settings.REDIRECT_URL,
            "client_id": self._settings.CLIENT_ID,
            "scope": self.SCOPE,
            "access_type": "offline",
            "prompt": "consent",
        }
        url_parts = urlsplit(self.AUTHORIZE_URL)
        return urlunparse(
            (
                url_parts.scheme,
                url_parts.netloc,
                url_parts.path,
                "",
                urlencode(query_params),
                "",
            )
        )

    async def get_access_token(self, query_params: dict) -> str:
        try:
            data = {
                "code": query_params[self.RESPONSE_TYPE],
                "client_id": self._settings.CLIENT_ID,
                "redirect_uri": self._settings.REDIRECT_URL,
                "client_secret": self._settings.CLIENT_SECRET,
                "grant_type": "authorization_code",
            }
        except KeyError as e:
            raise ProviderException(message=f"Missing required key: {e}")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = await self.post(url=self.TOKEN_URL, data=data, headers=headers)
            return response.get("access_token")
        except NetworkException as e:
            raise ProviderException(message=e.message)

    async def get_user_info(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            return await self.get(url=self.USER_INFO_URL, headers=headers)
        except NetworkException as e:
            raise ProviderException(message=e.message)
