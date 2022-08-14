import logging
from typing import Any, Union, Dict

from aiohttp import ClientSession, ContentTypeError

log = logging.getLogger(__name__)


class HttpException(Exception):
    def __init__(self, status: int, reason: str, error: Union[str, Dict[str, Any]]) -> None:
        self.status = status
        self.reason = reason

        if isinstance(error, dict):
            self.error = ', '.join([f'{k}={v}' for k, v in error.items()])
        else:
            self.error = error

        super().__init__(f'{self.status} {self.reason}: {self.error}')


async def request(url: str, session: ClientSession, method: str, res_method: str, *args, **kwargs) -> Any:
    r = await getattr(session, method)(url, *args, **kwargs)
    log.debug(f'{r.method} {r.url} {r.status} {r.reason}')
    if r.status != 200:
        try:
            error = await r.json()
        except ContentTypeError:
            error = await r.text()
        raise HttpException(r.status, r.reason, error)
    try:
        data = await getattr(r, res_method)()
    except UnicodeDecodeError:
        data = await getattr(r, res_method)(encoding='utf-8')
    return data


async def get(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> Any:
    return await request(url, session, 'get', res_method, *args, **kwargs)


async def post(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> Any:
    return await request(url, session, 'post', res_method, *args, **kwargs)
