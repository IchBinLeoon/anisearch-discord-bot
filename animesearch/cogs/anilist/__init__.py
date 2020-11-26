from animesearch.cogs.anilist.anilist import AniList
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(AniList(bot))
    logger.info('Loaded cog AniList')


def teardown():
    logger.info('Unloaded cog AniList')
