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
        super().__init__(status)


class EmptySearchImage(TraceMoeException):
    """Raised when the search image is empty."""

    def __init__(self, status: int) -> None:
        super().__init__(status)


class InvalidToken(TraceMoeException):
    """Raised when the token is invalid."""

    def __init__(self, status: int) -> None:
        super().__init__(status)


class RequestEntityTooLarge(TraceMoeException):
    """Raised when the image size is too large."""

    def __init__(self, status: int) -> None:
        super().__init__(status)


class TooManyRequests(TraceMoeException):
    """Raised when the requests are too fast."""

    def __init__(self, status: int) -> None:
        super().__init__(status)


class TraceMoeBackendError(TraceMoeException):
    """Raised when something went wrong in the trace.moe backend."""

    def __init__(self, status: int, msg: str) -> None:
        super().__init__(f'{status} - {msg}')


class TraceMoeClient:
    """Asynchronous wrapper client for the trace.moe API."""

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
        """Makes a request to the trace.moe API."""
        session = await self._session()
        response = await session.get(url)

        if response.status != 200:

            if response.status == 400:
                raise EmptySearchImage(response.status)

            if response.status == 403:
                raise InvalidToken(response.status)

            if response.status == 413:
                raise RequestEntityTooLarge(response.status)

            if response.status == 429:
                raise TooManyRequests(response.status)

            if response.status == 500 or response.status == 503:
                raise TraceMoeBackendError(response.status, await response.text())

            raise TraceMoeAPIError(response.status)

        data = await response.json()
        return data

    async def search(self, url: str) -> Union[Dict[str, Any], None]:
        """Searches an anime by image."""
        url = f'{TRACEMOE_BASE_URL}/search?url={url}'
        data = await self._request(url)
        if data.get('docs'):
            return data.get('docs')
        return None
