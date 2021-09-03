"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from typing import Any

from aiohttp import ClientSession, ContentTypeError

logger = logging.getLogger(__name__)


class RequestException(Exception):

    def __init__(self, status: int, reason: str, error: str) -> None:
        super().__init__(f'{status} {reason}: {error}')


async def request(url: str, session: ClientSession, method: str, res_method: str, *args, **kwargs) -> Any:
    r = await getattr(session, method)(url, *args, **kwargs)
    if r.status != 200:
        try:
            error = await r.json()
        except ContentTypeError:
            error = await r.text()
        raise RequestException(r.status, r.reason, str(error))
    return await getattr(r, res_method)()


async def get(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    return await request(url, session, 'get', res_method, *args, **kwargs)


async def post(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    return await request(url, session, 'post', res_method, *args, **kwargs)
