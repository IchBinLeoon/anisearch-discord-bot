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

from anisearch.utils.constants import KITSU_BASE_URL

log = logging.getLogger(__name__)


class KitsuException(Exception):
    """Base exception class for the Kitsu API wrapper."""


class KitsuAPIError(KitsuException):
    """Exception due to an error response from the Kitsu API."""

    def __init__(self, status: int) -> None:
        super().__init__(status)


class KitsuClient:
    """Asynchronous wrapper client for the Kitsu API."""

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
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
        """Gets an aiohttp session by creating it if it does not already exist or the previous session is closed."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, url: str) -> Dict[str, Any]:
        """Makes a request to the Kitsu API."""
        session = await self._session()
        response = await session.get(url)
        if response.status == 200:
            data = await response.json()
        else:
            raise KitsuAPIError(response.status)
        return data

    @staticmethod
    async def get_url(endpoint: str, parameters: str) -> str:
        """Creates the request url for the Kitsu endpoints."""
        request_url = f'{KITSU_BASE_URL}/{endpoint}{parameters}'
        return request_url

    async def user(self, username: str) -> Union[Dict[str, Any], None]:
        """Gets a user based on the given username."""
        parameters = f'?filter[name]={username}&include=stats,favorites'
        url = await self.get_url('users', parameters)
        data = await self._request(url=url)
        if data.get('data'):
            return data
        return None
