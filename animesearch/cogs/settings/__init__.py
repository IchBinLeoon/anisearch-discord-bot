from animesearch.cogs.settings.settings import Settings
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Settings(bot))
    logger.info('Loaded cog Settings')


def teardown():
    logger.info('Unloaded cog Settings')
