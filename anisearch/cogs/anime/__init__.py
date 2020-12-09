from anisearch.cogs.anime.anime import Anime
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Anime(bot))
    logger.info('Loaded cog Anime')
