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
from typing import Optional, Any, Dict, Union

import aiohttp

from anisearch.utils.constants import TRACEMOE_BASE_URL

log = logging.getLogger(__name__)


class TraceMoeException(Exception):
    """Base exception class for the trace.moe API wrapper."""


class TraceMoeAPIError(TraceMoeException):
    """Exception due to an error response from the trace.moe API."""

    def __init__(self, status: int) -> None:
        """
        Initializes the TraceMoeAPIError exception.

        Args:
            status (int): The status code.
        """
        super().__init__(status)


class TraceMoeError(TraceMoeException):
    """Exceptions that do not involve the API."""


class TraceMoeClient:
    """
    Asynchronous wrapper client for the trace.moe API.
    This class is used to interact with the API.

    Attributes:
        session (aiohttp.ClientSession): An aiohttp session.
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        """
        Initializes the TraceMoeClient.

        Args:
            session (aiohttp.ClientSession, optional): An aiohttp session.
        """
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Closes the aiohttp session."""
        if self.session is not None:
            await self.session.close()

    async def _session(self) -> aiohttp.ClientSession:
        """
        Gets an aiohttp session by creating it if it does not already exist or the previous session is closed.

        Returns:
            aiohttp.ClientSession: An aiohttp session.
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, url: str) -> Dict[str, Any]:
        """
        Makes a request to the trace.moe API.

        Args:
            url (str): The url used for the request.

        Returns:
            dict: Dictionary with the data from the response.
        """
        session = await self._session()
        response = await session.get(url)
        if response.status == 200:
            data = await response.json()
        else:
            raise TraceMoeAPIError(response.status)
        return data

    async def search(self, url: str) -> Union[Dict[str, Any], None]:
        """
        Searches an anime by image.

        Args:
            url (str): The image url.

        Returns:
            list: Dictionaries with the data about the found anime entries.
        """
        url = f'{TRACEMOE_BASE_URL}/search?url={url}'
        data = await self._request(url)
        if data.get('docs'):
            return data.get('docs')
        return None
