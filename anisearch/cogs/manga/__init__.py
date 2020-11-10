from anisearch.bot import logger
from anisearch.cogs.manga.manga import Manga


def setup(bot):
    bot.add_cog(Manga(bot))
    logger.info('Loaded extension Manga')


def teardown():
    logger.info('Unloaded extension Manga')
