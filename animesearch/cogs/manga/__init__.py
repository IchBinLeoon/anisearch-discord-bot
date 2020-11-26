from animesearch.cogs.manga.manga import Manga
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Manga(bot))
    logger.info('Loaded cog Manga')


def teardown():
    logger.info('Unloaded cog Manga')
