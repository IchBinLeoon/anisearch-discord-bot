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

from anisearch.utils.constants import JIKAN_BASE_URL

log = logging.getLogger(__name__)


class JikanException(Exception):
    """
    Base exception class for the Jikan API wrapper.
    """


class JikanAPIError(JikanException):
    """
    Exception due to an error response from the Jikan API.
    """

    def __init__(self, type_: str, status: int, msg: str, error: str) -> None:
        """
        Initializes the JikanAPIError exception.

        Args:
            status (int): The status code.
        """
        super().__init__(f'{type_} - Status: {str(status)} - Message: {msg} - Error: {error}')


class JikanError(JikanException):
    """
    Exceptions that do not involve the API.
    """


class JikanClient:
    """
    Asynchronous wrapper client for the Jikan API.
    This class is used to interact with the API.

    Attributes:
        session (aiohttp.ClientSession): An aiohttp session.
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        """
        Initializes the JikanClient.

        Args:
            session (aiohttp.ClientSession, optional): An aiohttp session.
        """
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Closes the aiohttp session.
        """
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

    async def _request(self, url: str) -> Union[Dict[str, Any], None]:
        """
        Makes a request to the Jikan API.

        Args:
            url (str): The url used for the request.

        Returns:
            dict: Dictionary with the data from the response.

        Raises:
            JikanAPIError: If the response contains an error.
        """
        session = await self._session()
        response = await session.get(url)
        data = await response.json()
        if data.get('error'):
            if data.get('status') == 404:
                data = None
            else:
                raise JikanAPIError(data.get('type'), data.get('status'), data.get('message'), data.get('error'))
        return data

    @staticmethod
    async def get_url(endpoint: str, parameters: str) -> str:
        """
        Creates the request url for the Jikan endpoints.

        Args:
            endpoint (str): The API endpoint.
            parameters (str): The query parameters.
        """
        request_url = f'{JIKAN_BASE_URL}/{endpoint}/{parameters}'
        return request_url

    async def user(self, username: str) -> Union[Dict[str, Any], None]:
        """
        Gets a user based on the given username.

        Args:
            username (str): The username of the searched user.

        Returns:
            dict: Dictionary with the data about the requested user.
            None: If no user was found.
        """
        parameters = username
        url = await self.get_url('user', parameters)
        data = await self._request(url=url)
        if data:
            return data
        return None
