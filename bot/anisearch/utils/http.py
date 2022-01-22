import logging
from typing import Any

from aiohttp import ClientSession, ContentTypeError

logger = logging.getLogger(__name__)


class RequestException(Exception):

    def __init__(self, status: int, reason: str, error: str) -> None:
        super().__init__(f'{status} {reason}: {error}')


async def request(url: str, session: ClientSession, method: str, res_method: str, *args, **kwargs) -> Any:
    r = await getattr(session, method)(url, *args, **kwargs)
    logger.debug(f'{r.method} {r.url} {r.status} {r.reason}')
    if r.status != 200:
        try:
            error = await r.json()
        except ContentTypeError:
            error = await r.text()
        raise RequestException(r.status, r.reason, str(error))
    try:
        data = await getattr(r, res_method)()
    except UnicodeDecodeError:
        data = await getattr(r, res_method)(encoding='utf-8')
    return data


async def get(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    return await request(url, session, 'get', res_method, *args, **kwargs)


async def post(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    return await request(url, session, 'post', res_method, *args, **kwargs)
