from animesearch.cogs.anime.anime import Anime
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Anime(bot))
    logger.info('Loaded cog Anime')


def teardown():
    logger.info('Unloaded cog Anime')
