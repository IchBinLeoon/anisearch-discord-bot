from anisearch.cogs.anime.anime import Anime
from anisearch.bot import logger


def setup(bot):
    bot.add_cog(Anime(bot))
    logger.info('Loaded extension Anime')


def teardown():
    logger.info('Unloaded extension Anime')
