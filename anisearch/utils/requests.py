import aiohttp
from jikanpy import AioJikan
import requests


async def anilist_request(query, variables):
    api = 'https://graphql.anilist.co'
    request_json = {'query': query, 'variables': variables}
    async with aiohttp.ClientSession() as session:
        async with session.post(api, json=request_json) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def myanimelist_request(request, search):
    if request == 'user':
        aio_jikan = AioJikan()
        try:
            data = await aio_jikan.user(username=search)
        except:
            data = None
        await aio_jikan.close()
        return data


async def kitsu_request(request, search):
    if request == 'user':
        response = requests.get('https://kitsu.io/api/edge/users?filter[name]={}&include=stats,favorites'
                                .format(search))
        if response.status_code == 200:
            return response.json()
        else:
            return None
