from animesearch.cogs.profile.profile import Profile
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Profile(bot))
    logger.info('Loaded cog Profile')


def teardown():
    logger.info('Unloaded cog Profile')
