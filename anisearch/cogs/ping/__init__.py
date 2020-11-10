from anisearch.bot import logger
from anisearch.cogs.ping.ping import Ping


def setup(bot):
    bot.add_cog(Ping(bot))
    logger.info('Loaded extension Ping')


def teardown():
    logger.info('Unloaded extension Ping')
