from anisearch.cogs.random.random import Random
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Random(bot))
    logger.info('Loaded cog Random')


def teardown():
    logger.info('Unloaded cog Random')
