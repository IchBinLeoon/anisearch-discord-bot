from anisearch.cogs.trace.trace import Trace
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Trace(bot))
    logger.info('Loaded cog Trace')


def teardown():
    logger.info('Unloaded cog Trace')
