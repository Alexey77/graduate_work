import httpx

from .exception import NetworkException
from .inetworking import INetworkClient


class HttpxNetworkClient(INetworkClient):
    async def get(self, url: str, params: dict = None, headers: dict = None) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise NetworkException(message=f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            raise NetworkException(message=f"Request error occurred: {e}")

    async def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise NetworkException(message=f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            raise NetworkException(message=f"Request error occurred: {e}")
