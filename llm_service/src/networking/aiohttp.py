import aiohttp
from aiohttp import ClientError, ClientResponseError
from aiohttp_socks import ProxyConnector
from core.config import ProxySocks5
from core.logger import get_logger

from .exception import NetworkException

logger = get_logger(__name__)


async def send_post(url: str, data: dict, headers: dict, proxy: ProxySocks5 | None = None) -> tuple[int, dict | str]:
    """Send POST request using aiohttp, optionally with SOCKS5 proxy."""
    try:
        logger.info(f"Sending POST request to {url} with data={data} and headers={headers}")

        connector = None
        if proxy:
            # Use ProxyConnector for SOCKS5 proxy
            proxy_url = proxy.to_proxy_url()
            connector = ProxyConnector.from_url(proxy_url)

        async with aiohttp.ClientSession(connector=connector) as session, session.post(url, json=data, headers=headers) as response:
            status_code = response.status
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                result = await response.json()
            else:
                result = await response.text()

            logger.info(f"POST request to {url} succeeded with response: {result}")
            return status_code, result
    except ClientResponseError as e:
        logger.error(f"HTTP error occurred during POST request to {url}: {e}")
        msg = f"HTTP error occurred: {e}"
        raise NetworkException(msg)
    except ClientError as e:
        logger.error(f"Request error occurred during POST request to {url}: {e}")
        msg = f"Request error occurred: {e}"
        raise NetworkException(msg)
