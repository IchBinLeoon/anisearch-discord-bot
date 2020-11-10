from anisearch.bot import logger
from anisearch.cogs.anilist.anilist import AniList


def setup(bot):
    bot.add_cog(AniList(bot))
    logger.info('Loaded extension AniList')


def teardown():
    logger.info('Unloaded extension AniList')
