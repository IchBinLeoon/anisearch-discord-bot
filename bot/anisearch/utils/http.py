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

from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class RequestException(Exception):
    """Exception due to an request error."""

    def __init__(self, status: int) -> None:
        super().__init__(status)


async def request(url: str, session: ClientSession, method: str, res_method: str, *args, **kwargs) -> Any:
    """Performs a request."""
    r = await getattr(session, method)(url, *args, **kwargs)
    if r.status != 200:
        raise RequestException(r.status)
    return await getattr(r, res_method)()


async def get(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    """Performs an HTTP GET request."""
    return await request(url, session, 'get', res_method, *args, **kwargs)


async def post(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    """Performs an HTTP POST request."""
    return await request(url, session, 'post', res_method, *args, **kwargs)
