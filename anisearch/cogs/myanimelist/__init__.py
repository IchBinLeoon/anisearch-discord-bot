from anisearch.bot import logger
from anisearch.cogs.myanimelist.myanimelist import MyAnimeList


def setup(bot):
    bot.add_cog(MyAnimeList(bot))
    logger.info('Loaded extension MyAnimeList')


def teardown():
    logger.info('Unloaded extension MyAnimeList')
