import aiohttp


async def trace(url):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://trace.moe/api/search?url={url}') as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def source(url):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://saucenao.com/search.php?db=999&url={url}') as response:
            if response.status == 200:
                return await response.text()
            else:
                return None
