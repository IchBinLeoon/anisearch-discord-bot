from anisearch.cogs.manga.manga import Manga
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Manga(bot))
    logger.info('Loaded cog Manga')
