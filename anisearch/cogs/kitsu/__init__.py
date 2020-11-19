from anisearch.cogs.kitsu.kitsu import Kitsu
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Kitsu(bot))
    logger.info('Loaded cog Kitsu')


def teardown():
    logger.info('Unloaded cog Kitsu')
