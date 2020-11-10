from anisearch.bot import logger
from anisearch.cogs.prefix.prefix import Prefix


def setup(bot):
    bot.add_cog(Prefix(bot))
    logger.info('Loaded extension Prefix')


def teardown():
    logger.info('Unloaded extension Prefix')
