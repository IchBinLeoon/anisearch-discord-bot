import dbl
from discord.ext import commands

import anisearch
from config import config


class TopGG(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.token = config.TOPGG
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        anisearch.logger.info('TopGG server count posted (%s)' % self.dblpy.guild_count())


def setup(client):
    client.add_cog(TopGG(client))
    anisearch.logger.info('Loaded extension TopGG')


def teardown():
    anisearch.logger.info('Unloaded extension TopGG')
