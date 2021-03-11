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

from quart import Quart, render_template
from discord.ext import ipc

app = Quart(__name__)
ipc = ipc.Client(secret_key='anisearch-discord-bot', host='bot', port=8765, multicast_port=20000)


@app.route('/')
async def index():
    data = {
        'ready': await request('is_ready'),
        'guilds': await request('get_guild_count'),
        'users': await request('get_user_count'),
        'channels': await request('get_channel_count'),
        'uptime': await request('get_uptime'),
        'shards': await request('get_shard_count'),
        'latency': await request('get_latency'),
        'cogs_count': await request('get_cogs_count'),
        'cogs_loaded': await request('get_cogs_loaded')
    }
    return await render_template('index.html', **data)


@app.route('/logs')
async def logs():
    data = await request('get_logs')
    if data is not None:
        data = data.split('\n')
    return await render_template('logs.html', data=data)


async def request(endpoint: str):
    """
    Makes a request to the IPC server.

    Args:
        endpoint (str): The endpoint to request on the server.
    """
    try:
        return await ipc.request(endpoint)
    except ConnectionResetError:
        value = '-'
    except Exception as e:
        app.logger.exception(e)
        value = '-'
    if endpoint == 'is_ready':
        return False
    if endpoint == 'get_logs':
        return None
    return value


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
