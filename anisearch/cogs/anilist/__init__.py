from anisearch.cogs.anilist.anilist import AniList
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(AniList(bot))
    logger.info('Loaded cog AniList')
