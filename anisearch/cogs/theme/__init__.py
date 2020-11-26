from anisearch.cogs.theme.theme import Theme
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Theme(bot))
    logger.info('Loaded cog Theme')


def teardown():
    logger.info('Unloaded cog Theme')
