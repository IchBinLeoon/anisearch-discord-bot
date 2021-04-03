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

import json
import logging

from aiohttp import web, web_request

log = logging.getLogger(__name__)


class Server:
    """
    The API server.
    """

    def __init__(self, bot, host: str, port: int, secret_key: str) -> None:
        """
        Initializes the API server.

        Args:
            bot: The bot instance.
            host (str): The API host.
            port (int): The API port.
            secret_key (str): The API secret key.
        """
        self.bot = bot
        self.loop = bot.loop
        self.host = host
        self.port = port
        self.secret_key = secret_key
        self._server = None

    async def handle(self, request: web_request.Request) -> web.Response:
        """
        Handles the API requests.

        Args:
            request (web_request.Request): The request.
        """
        if not request.headers or request.headers.get('Authentication') != self.secret_key:
            status = 403
            response = {'error': '403 Forbidden', 'code': status}
        else:
            try:
                q = request.query
                if q.get('type') == 'stats':
                    status = 200
                    response = {
                        'ready': self.bot.is_ready(),
                        'guilds': self.bot.get_guild_count(),
                        'users': self.bot.get_user_count(),
                        'channels': self.bot.get_channel_count(),
                        'uptime': round(self.bot.get_uptime()),
                        'shards': self.bot.shard_count,
                        'latency': round(self.bot.latency, 6),
                        'cogs': len(self.bot.cogs),
                    }
                elif q.get('type') == 'logs':
                    status = 200
                    response = {
                        'logs': str(self.bot.log_stream.getvalue())
                    }
                else:
                    status = 400
                    response = {'error': '400 Bad Request', 'code': status}
            except Exception as e:
                log.exception(e)
                status = 500
                response = {'error': '500 Internal Server Error', 'code': status}
        return web.Response(text=json.dumps(response), status=status)

    async def _start(self) -> None:
        """
        Starts the API server.
        """
        runner = web.AppRunner(self._server)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        self.bot.dispatch('api_ready', self.host, self.port)

    def start(self) -> None:
        """
        Starts the API server.
        """
        logger = logging.getLogger('aiohttp.access')
        logger.setLevel(logging.ERROR)

        self._server = web.Application()
        self._server.router.add_route('GET', '/api', self.handle)

        self.loop.run_until_complete(self._start())
