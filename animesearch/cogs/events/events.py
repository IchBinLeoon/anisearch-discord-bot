import dbl
from discord.ext import commands
from animesearch import config
from animesearch.utils.logger import logger


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.token = config.TopGG
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        logger.info('TopGG server count posted ({})'.format(self.dblpy.guild_count()))
