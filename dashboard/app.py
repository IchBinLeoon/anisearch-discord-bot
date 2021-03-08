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

from config import IPC_SECRET_KEY

app = Quart(__name__)
ipc = ipc.Client(secret_key=IPC_SECRET_KEY, host='bot', port=8765, multicast_port=20000)


@app.route('/')
async def index():
    data = {
        'guilds': await ipc.request('get_guild_count'),
        'users': await ipc.request('get_user_count'),
        'channels': await ipc.request('get_channel_count'),
        'uptime': await ipc.request('get_uptime'),
        'shards': await ipc.request('get_shard_count'),
        'latency': await ipc.request('get_latency')
    }
    return await render_template('index.html', **data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
