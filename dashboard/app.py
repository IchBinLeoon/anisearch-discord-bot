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

from quart import Quart, render_template, request, redirect, url_for
from discord.ext import ipc

from config import IPC_SECRET_KEY, IPC_HOST, IPC_PORT, APP_HOST, APP_PORT, IPC_MULTICAST_PORT

app = Quart(__name__)
ipc_client = ipc.Client(secret_key=IPC_SECRET_KEY, host=IPC_HOST, port=int(IPC_PORT), multicast_port=IPC_MULTICAST_PORT)


@app.route('/')
async def index():
    if request.args.get('reconnect') == 'true':
        try:
            if not ipc_client.session.closed:
                await ipc_client.session.close()
            await ipc_client.init_sock()
        except Exception as e:
            app.logger.exception(e)
        return redirect(url_for('index'))
    data = {
        'ready': await ipc_request('is_ready'),
        'guilds': await ipc_request('get_guild_count'),
        'users': await ipc_request('get_user_count'),
        'channels': await ipc_request('get_channel_count'),
        'uptime': await ipc_request('get_uptime'),
        'shards': await ipc_request('get_shard_count'),
        'latency': await ipc_request('get_latency'),
        'cogs': await ipc_request('get_cogs'),
    }
    return await render_template('index.html', **data)


@app.route('/logs')
async def logs():
    data = await ipc_request('get_logs')
    if data is not None:
        data = data.split('\n')
    return await render_template('logs.html', data=data)


async def ipc_request(endpoint: str):
    """
    Makes a request to the IPC server.

    Args:
        endpoint (str): The endpoint to request on the server.
    """
    try:
        return await ipc_client.request(endpoint)
    except ConnectionResetError:
        value = '-'
    except Exception as e:
        app.logger.exception(e)
        value = '-'
    if endpoint == 'is_ready':
        return False
    if endpoint == 'get_logs':
        return None
    if endpoint == 'get_uptime':
        return 'null'
    return value


if __name__ == '__main__':
    app.run(host=APP_HOST, port=int(APP_PORT))
