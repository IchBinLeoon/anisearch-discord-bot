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

import aiohttp
from jikanpy import AioJikan
from jikanpy import JikanException


async def anilist_request(query, variables):
    api = 'https://graphql.anilist.co'
    request_json = {'query': query, 'variables': variables}
    async with aiohttp.ClientSession() as session:
        async with session.post(api, json=request_json) as response:
            if response.status == 200:
                return await response.json()
            return None


async def myanimelist_request(request, search):
    if request == 'user':
        aio_jikan = AioJikan()
        try:
            data = await aio_jikan.user(username=search)
        except JikanException:
            data = None
        await aio_jikan.close()
        return data


async def kitsu_request(request, search):
    if request == 'user':
        api = f'https://kitsu.io/api/edge/users?filter[name]={search}&include=stats,favorites'
        async with aiohttp.ClientSession() as session:
            async with session.get(api) as response:
                if response.status == 200:
                    return await response.json()
                return None


async def tracemoe_request(url):
    api = f'https://trace.moe/api/search?url={url}'
    async with aiohttp.ClientSession() as session:
        async with session.post(api) as response:
            if response.status == 200:
                return await response.json()
            return None


async def saucenao_request(url):
    api = f'http://saucenao.com/search.php?db=999&url={url}'
    async with aiohttp.ClientSession() as session:
        async with session.post(api) as response:
            if response.status == 200:
                return await response.text()
            return None


async def animethemes_request(anime):
    api = f'https://animethemes-api.herokuapp.com/api/v1/s/{anime}'
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            if response.status == 200:
                return await response.json()
            return None
