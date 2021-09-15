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

from anisearch.config import BOT_LEVEL

log = logging.getLogger(__name__)


class Server:

    def __init__(self, bot, host: str, port: int, secret_key: str) -> None:
        self.bot = bot
        self.loop = bot.loop
        self.host = host
        self.port = port
        self.secret_key = secret_key
        self._server = None

    async def handle_info(self, request: web_request.Request) -> web.Response:
        if not request.headers or request.headers.get('Authentication') != self.secret_key:
            status = 403
            response = {'error': '403 Forbidden', 'code': status}
        else:
            try:
                q = request.query
                if q.get('type') == 'stats':
                    status = 200
                    response = {
                        'is_ready': self.bot.is_ready(),
                        'guild_count': self.bot.get_guild_count(),
                        'user_count': self.bot.get_user_count(),
                        'channel_count': self.bot.get_channel_count(),
                        'uptime': self.bot.get_uptime(),
                        'shard_count': self.bot.shard_count,
                        'latency': self.bot.latency,
                        'cog_count': len(self.bot.cogs),
                    }
                elif q.get('type') == 'logs':
                    status = 200
                    response = {
                        'logs': str(self.bot.log_stream.getvalue())
                    }
                elif q.get('type') == 'shards':
                    shards = []
                    for i in self.bot.shards:
                        s = self.bot.get_shard(i)
                        shard = {
                            'id': s.id,
                            'shard_count': s.shard_count,
                            'is_closed': s.is_closed(),
                            'latency': s.latency,
                            'is_ws_ratelimited': s.is_ws_ratelimited()
                        }
                        shards.append(shard)
                    status = 200
                    response = {
                        'shards': shards
                    }
                else:
                    status = 400
                    response = {'error': '400 Bad Request', 'code': status}
            except Exception as e:
                log.exception(e)
                status = 500
                response = {'error': '500 Internal Server Error', 'code': status}
        return web.Response(text=json.dumps(response), status=status)

    async def handle_notification(self, request: web_request.Request) -> web.Response:
        if not request.headers or request.headers.get('Authentication') != self.secret_key:
            status = 403
            response = {'error': '403 Forbidden', 'code': status}
        else:
            try:
                q = request.query
                if q.get('type') == 'episode':
                    status = 200
                    response = {
                        'status': status,
                    }
                    data = await request.json()
                    log.info(f'New episode notification: {data.get("romaji")} [{data.get("id")}]')
                    cog = self.bot.get_cog('Notification')
                    if cog is None:
                        log.warning('Notification cog has not been loaded: Cannot send episode notification')
                    else:
                        await cog.send_episode_notification(data)
                else:
                    status = 400
                    response = {'error': '400 Bad Request', 'code': status}
            except Exception as e:
                log.exception(e)
                status = 500
                response = {'error': '500 Internal Server Error', 'code': status}
        return web.Response(text=json.dumps(response), status=status)

    async def _start(self) -> None:
        runner = web.AppRunner(self._server)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        self.bot.dispatch('api_ready', self.host, self.port)

    def start(self) -> None:
        if not logging.getLevelName(BOT_LEVEL) is logging.DEBUG:
            logger = logging.getLogger('aiohttp.access')
            logger.setLevel(logging.ERROR)

        self._server = web.Application()

        self._server.router.add_route('GET', '/api/info', self.handle_info)
        self._server.router.add_route('POST', '/api/notification', self.handle_notification)

        self.loop.run_until_complete(self._start())
