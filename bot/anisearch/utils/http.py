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
    """
    Exception due to an request error.
    """

    def __init__(self, status: int) -> None:
        """
        Initializes the RequestException exception.

        Args:
            status (int): The status code.
        """
        super().__init__(status)


class HTTPSession(ClientSession):
    """
    Abstract class for an aiohttp session.
    """

    def __init__(self, loop=None):
        """
        Initializes the HTTPSession.
        """
        super().__init__(loop=loop)


async def request(url: str, session: ClientSession, method: str, res_method: str, *args, **kwargs) -> Any:
    """
    Performs a request.

    Args:
        url (str): The request url.
        session (ClientSession): An aiohttp session.
        method (str): The request method.
        res_method (str): The response method.

    Returns:
        Any: The data from the response.

    Raises:
        RequestException: If an error occurs during the request.
    """
    r = await getattr(session, method)(url, *args, **kwargs)
    if r.status != 200:
        raise RequestException(r.status)
    return await getattr(r, res_method)()


async def get(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    """
    Performs an HTTP GET request.

    Args:
        url (str): The request url.
        session (ClientSession): An aiohttp session.
        res_method (str): The response method.

    Returns:
        request()
    """
    return await request(url, session, 'get', res_method, *args, **kwargs)


async def post(url: str, session: ClientSession, res_method: str, *args, **kwargs) -> request:
    """
    Performs an HTTP POST request.

    Args:
        url (str): The request url.
        session (ClientSession): An aiohttp session.
        res_method (str): The response method.

    Returns:
        request()
    """
    return await request(url, session, 'post', res_method, *args, **kwargs)
