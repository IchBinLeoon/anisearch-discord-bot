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
from typing import Optional, Any, Dict, Union, List

import aiohttp
from bs4 import BeautifulSoup

from anisearch.utils.constants import ANIMENEWSNETWORK_NEWS_FEED_ENDPOINT

log = logging.getLogger(__name__)


class AnimeNewsNetworkException(Exception):
    pass


class AnimeNewsNetworkFeedError(AnimeNewsNetworkException):

    def __init__(self, status: int) -> None:
        super().__init__(status)


class AnimeNewsNetworkClient:

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()

    async def _session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, url: str) -> str:
        session = await self._session()
        response = await session.get(url)
        if response.status == 200:
            data = await response.text()
        else:
            raise AnimeNewsNetworkFeedError(response.status)
        return data

    @staticmethod
    async def _parse_feed(text: str, count: int) -> Union[List[Dict[str, Any]], None]:
        soup = BeautifulSoup(text, 'html.parser')
        items = soup.find_all('item')
        if items:
            data = []
            for item in items:
                if len(data) >= count:
                    break
                feed = {
                    'title': item.find('title').text,
                    'link': item.find('guid').text,
                    'description': item.find('description').text,
                    'category': item.find('category').text if item.find('category') else None,
                    'date': item.find('pubdate').text
                }
                data.append(feed)
            return data
        return None

    async def news(self, count: int) -> Union[List[Dict[str, Any]], None]:
        text = await self._request(ANIMENEWSNETWORK_NEWS_FEED_ENDPOINT)
        data = await self._parse_feed(text=text, count=count)
        if data:
            return data
        return None
