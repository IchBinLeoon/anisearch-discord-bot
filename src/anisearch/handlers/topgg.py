import dbl
from discord.ext import commands, tasks

import main
from config import config


class TopGG(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.token = config.TOPGG
        self.dblpy = dbl.DBLClient(self.client, self.token)

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        try:
            await self.dblpy.post_guild_count()
            main.logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
        except Exception as e:
            main.logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))


def setup(client):
    client.add_cog(TopGG(client))
    main.logger.info('Loaded extension TopGG')


def teardown():
    main.logger.info('Unloaded extension TopGG')
