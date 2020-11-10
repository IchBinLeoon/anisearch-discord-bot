from anisearch.bot import logger
from anisearch.cogs.random.random import Random


def setup(bot):
    bot.add_cog(Random(bot))
    logger.info('Loaded extension Random')


def teardown():
    logger.info('Unloaded extension Random')
