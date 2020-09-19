import dbl
from discord.ext import commands

import main
from config import config


class TopGG(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.token = config.TOPGG
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    async def on_guild_post(self):
        main.logger.info('TopGG server count posted (%s)' % self.dblpy.guild_count())


def setup(client):
    client.add_cog(TopGG(client))
    main.logger.info('Loaded extension TopGG')


def teardown():
    main.logger.info('Unloaded extension TopGG')
