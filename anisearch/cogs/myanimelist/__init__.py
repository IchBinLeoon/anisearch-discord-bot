from anisearch.cogs.myanimelist.myanimelist import MyAnimeList
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(MyAnimeList(bot))
    logger.info('Loaded cog MyAnimeList')
