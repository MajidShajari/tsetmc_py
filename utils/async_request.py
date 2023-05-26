import asyncio
from typing import Optional
import aiohttp

from utils import custom_logger

_logger = custom_logger.main_logger


async def get_request(url: str, retry: int = 10, timeout: int = 10) -> Optional[str]:
    """
    Send an HTTP GET request and return the response text.

    If the request fails with a status code in the status_forcelist (500, 502, 503, 504),
    retry the request up to `retry` times with a delay of 2 seconds between retries.

    Return `None` if the request fails with an HTTP error other than those in the status_forcelist.
    """
    status_forcelist = (500, 502, 503, 504)
    timeout = aiohttp.ClientTimeout(total=timeout)  # type: ignore
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for _ in range(retry):
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text(encoding="utf-8")
                    if response.status in status_forcelist:
                        _logger.debug(
                            "Server not responding, retrying... URL: %s", url.encode())
                        await asyncio.sleep(2)
                    else:
                        _logger.warning("HTTP error: %s URL: %s",
                                        response.status, url.encode())
                        return None
            except (asyncio.TimeoutError, aiohttp.ClientError):
                _logger.debug(
                    "Connection error, retrying... URL: %s", url.encode())
                await asyncio.sleep(2)
        _logger.warning(
            "Request failed after %s retries URL: %s", retry, url.encode())
        return None
