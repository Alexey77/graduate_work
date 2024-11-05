import aiohttp
from aiohttp import ClientError, ClientResponseError

from .exception import NetworkException
from .inetworking import INetworkClient


class AiohttpNetworkClient(INetworkClient):
    async def get(self, url: str, params: dict = None, headers: dict = None) -> dict:
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(url, params=params, headers=headers) as response,
            ):
                response.raise_for_status()
                return await response.json()
        except ClientResponseError as e:
            raise NetworkException(message=f"HTTP error occurred: {e}")
        except ClientError as e:
            raise NetworkException(message=f"Request error occurred: {e}")

    async def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(url, data=data, headers=headers) as response,
            ):
                response.raise_for_status()
                return await response.json()
        except ClientResponseError as e:
            raise NetworkException(message=f"HTTP error occurred: {e}")
        except ClientError as e:
            raise NetworkException(message=f"Request error occurred: {e}")
