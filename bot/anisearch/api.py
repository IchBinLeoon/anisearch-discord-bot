import logging
import time

from aiohttp import web, web_request

log = logging.getLogger(__name__)


class Server:
    def __init__(self, bot) -> None:
        self.bot = bot
        self._runner = None

    async def _handle_stats(self, request: web_request.Request) -> web.Response:
        stats = {
            'guild_count': len(self.bot.guilds),
            'user_count': sum([i.member_count for i in self.bot.guilds]),
            'channel_count': sum([len(i.channels) for i in self.bot.guilds]),
            'uptime': time.time() - self.bot.start_time,
            'shard_count': self.bot.shard_count,
            'latency': self.bot.latency,
        }
        return web.json_response({'stats': stats})

    async def _handle_shards(self, request: web_request.Request) -> web.Response:
        shards = []
        for i in self.bot.shards:
            shard = self.bot.get_shard(i)
            info = {
                'id': shard.id,
                'shard_count': shard.shard_count,
                'is_closed': shard.is_closed(),
                'latency': shard.latency,
                'is_ws_ratelimited': shard.is_ws_ratelimited(),
            }
            shards.append(info)
        return web.json_response({'shards': shards})

    async def _handle_log(self, request: web_request.Request) -> web.Response:
        response = {'log': self.bot.log_stream.getvalue()}
        return web.json_response(response)

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()

    async def start(self, host: str, port: int) -> None:
        app = web.Application()

        app.router.add_route('GET', '/api/v1/bot/stats', self._handle_stats)
        app.router.add_route('GET', '/api/v1/bot/shards', self._handle_shards)
        app.router.add_route('GET', '/api/v1/bot/log', self._handle_log)

        self._runner = web.AppRunner(app)
        await self._runner.setup()

        site = web.TCPSite(self._runner, host, port)
        await site.start()

        self.bot.dispatch('api_ready', host, port)
