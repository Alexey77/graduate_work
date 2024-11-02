import aiohttp
import pytest_asyncio
from functional.settings import service_settings


@pytest_asyncio.fixture(name='http_session', scope='function')
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='make_get_http_request')
def make_get_http_request(http_session: aiohttp.ClientSession):
    async def inner(endpoint: str, params: dict = None, **kwargs):
        url = service_settings.service_base_api_url + endpoint
        async with http_session.get(url, json=params or {}, **kwargs) as response:
            body = await response.json()
            status = response.status
        return status, body

    return inner


@pytest_asyncio.fixture(name='make_post_http_request')
def make_post_http_request(http_session: aiohttp.ClientSession):
    async def inner(endpoint: str, headers: dict = None, params: dict = None, **kwargs):
        url = service_settings.service_base_api_url + endpoint
        async with http_session.post(url, headers=headers, json=params or {}, **kwargs) as response:
            body = await response.json()
            status = response.status
        return status, body

    return inner


@pytest_asyncio.fixture(name='make_patch_http_request')
def make_patch_http_request(http_session: aiohttp.ClientSession):
    async def inner(endpoint: str, headers: dict = None, json_data: dict = None, **kwargs):
        url = service_settings.service_base_api_url + endpoint
        if headers is None:
            headers = {}
        async with http_session.patch(url, json=json_data or {}, headers=headers, **kwargs) as response:
            body = await response.json()
            status = response.status

        return status, body

    return inner


@pytest_asyncio.fixture(name='make_put_http_request')
def make_put_http_request(http_session: aiohttp.ClientSession):
    async def inner(endpoint: str, headers: dict = None, json_data: dict = None, **kwargs):
        url = service_settings.service_base_api_url + endpoint
        if headers is None:
            headers = {}
        async with http_session.put(url, json=json_data or {}, headers=headers, **kwargs) as response:
            body = await response.json()
            status = response.status

        return status, body

    return inner


@pytest_asyncio.fixture(name='make_delete_http_request')
def make_delete_http_request(http_session: aiohttp.ClientSession):
    async def inner(endpoint: str, headers: dict = None, json_data: dict = None, **kwargs):
        url = service_settings.service_base_api_url + endpoint
        if headers is None:
            headers = {}
        async with http_session.delete(url, json=json_data or {}, headers=headers, **kwargs) as response:
            body = await response.json()
            status = response.status

        return status, body

    return inner
