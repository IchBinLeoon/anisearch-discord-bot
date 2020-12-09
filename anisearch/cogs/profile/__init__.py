from anisearch.cogs.profile.profile import Profile
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Profile(bot))
    logger.info('Loaded cog Profile')
