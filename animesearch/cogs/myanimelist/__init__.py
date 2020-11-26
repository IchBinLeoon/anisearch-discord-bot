from animesearch.cogs.myanimelist.myanimelist import MyAnimeList
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(MyAnimeList(bot))
    logger.info('Loaded cog MyAnimeList')


def teardown():
    logger.info('Unloaded cog MyAnimeList')
