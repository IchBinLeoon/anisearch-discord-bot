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
from typing import Optional, Any, Dict, List

import aiohttp

from anisearch.utils.constants import ANIMETHEMES_BASE_URL

log = logging.getLogger(__name__)


class AnimeThemesException(Exception):
    """
    Base exception class for the AnimeThemes API wrapper.
    """


class AnimeThemesAPIError(AnimeThemesException):
    """
    Exception due to an error response from the AnimeThemes API.
    """

    def __init__(self, msg: str, status: int) -> None:
        """
        Initializes the AnimeThemesAPIError exception.

        Args:
            msg (str): The error message.
            status (int): The status code.
        """
        super().__init__(msg + ' - Status: ' + str(status))


class AnimeThemesError(AnimeThemesException):
    """
    Exceptions that do not involve the API.
    """


class AnimeThemesClient:
    """
    Asynchronous wrapper client for the AnimeThemes API.
    This class is used to interact with the API.

    Attributes:
        session (aiohttp.ClientSession): An aiohttp session.
        headers (dict): HTTP headers used in the request.
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None, headers: Dict[str, Any] = None) -> None:
        """
        Initializes the AnimeThemesClient.

        Args:
            session (aiohttp.ClientSession, optional): An aiohttp session.
            headers (dict, optional): HTTP headers used in the request.
        """
        self.session = session
        if headers:
            self.headers = headers
        else:
            self.headers = {}

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

    async def _request(self, url: str) -> Dict[str, Any]:
        """
        Makes a request to the AnimeThemes API.

        Args:
            url (str): The url used for the request.

        Returns:
            dict: Dictionary with the data from the response.

        Raises:
            AnimeThemesAPIError: If the response contains an error.
        """
        session = await self._session()
        response = await session.get(url=url, headers=self.headers)
        data = await response.json()
        if data.get('errors'):
            raise AnimeThemesAPIError(data.get('errors')[0]['detail'], data.get('errors')[0]['status'])
        return data

    @staticmethod
    async def get_url(endpoint: str, parameters: str) -> str:
        """
        Creates the request url for the animethemes endpoints.

        Args:
            endpoint (str): The API endpoint.
            parameters (str): The query parameters.
        """
        request_url = f'{ANIMETHEMES_BASE_URL}/{endpoint}{parameters}'
        return request_url

    async def search(self, query: str, limit: Optional[int] = 5, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Returns relevant resources by search criteria.

        Args:
            query (str): The search query.
            limit (int, optional): The number of each resource to return (1-5).
            fields (str, optional): The list of resources to include.

        Returns:
            dict: The data about the requested resources.
        """
        q = '%20'.join(query.split())
        if fields is None:
            fields = []
        parameters = f'?q={q}&limit={limit}&fields={"%2C".join(fields)}'
        url = await self.get_url('search', parameters)
        data = await self._request(url=url)
        return data
