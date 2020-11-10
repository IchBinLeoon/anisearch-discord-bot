import dbl
from discord.ext import commands

from anisearch import config
from anisearch.bot import logger


class TopGG(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.token = config.TOPGG
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        logger.info('TopGG server count posted (%s)' % self.dblpy.guild_count())
