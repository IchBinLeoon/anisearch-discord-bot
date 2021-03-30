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

from anisearch.utils.constants import SAUCENAO_BASE_URL

log = logging.getLogger(__name__)


class SauceNAOException(Exception):
    """
    Base exception class for the SauceNAO API wrapper.
    """


class SauceNAOAPIError(SauceNAOException):
    """
    Exception due to an error response from the SauceNAO API.
    """

    def __init__(self, status: int) -> None:
        """
        Initializes the SauceNAOAPIError exception.

        Args:
            status (int): The status code.
        """
        super().__init__(status)


class SauceNAOError(SauceNAOException):
    """
    Exceptions that do not involve the API.
    """


class SauceNAOClient:
    """
    Asynchronous wrapper client for the SauceNAO API.
    This class is used to interact with the API.

    Attributes:
        session (aiohttp.ClientSession): An aiohttp session.
        api_key (str): The SauceNAO API key.
        db (int): Index num or 999 for all.
        output_type (int): The output type (0=normal html, 1=xml api, 2=json api).
        numres (int): Number of the results requested.
        long_remaining (int): Remaining daily API requests.
    """

    def __init__(self, api_key: str, db: int, output_type: int, numres: int,
                 session: Optional[aiohttp.ClientSession] = None) -> None:
        """
        Initializes the SauceNAOClient.

        Args:
            session (aiohttp.ClientSession, optional): An aiohttp session.
            api_key (str): The SauceNAO API key.
            db (int): Index num or 999 for all.
            output_type (int): The output type (0=normal html, 1=xml api, 2=json api).
            numres (int): Number of the results requested.
        """
        self.session = session
        self.api_key = api_key
        self.db = db
        self.output_type = output_type
        self.numres = numres
        self.long_remaining = None

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
        Makes a request to the SauceNAO API.

        Args:
            url (str): The url used for the request.

        Returns:
            dict: Dictionary with the data from the response.

        Raises:
            SauceNAOAPIError: If the response contains an error.
        """
        session = await self._session()
        response = await session.get(url)
        if response.status == 200:
            data = await response.json()
            self.long_remaining = data.get('header')['long_remaining']
        else:
            raise SauceNAOAPIError(response.status)
        return data

    async def search(self, url: str) -> Union[Dict[str, Any], None]:
        """
        Look up the source of an image by url.

        Args:
            url (str): The image url.

        Returns:
            list: Dictionaries with the data about the found entries.
        """
        url = f'{SAUCENAO_BASE_URL}?db={str(self.db)}&output_type={str(self.output_type)}&numres={str(self.numres)}' \
              f'&api_key={str(self.api_key)}&url={url}'
        data = await self._request(url)
        if data.get('results'):
            return data.get('results')
        return None
