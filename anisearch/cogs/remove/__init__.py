from anisearch.bot import logger
from anisearch.cogs.remove.remove import Remove


def setup(bot):
    bot.add_cog(Remove(bot))
    logger.info('Loaded extension Remove')


def teardown():
    logger.info('Unloaded extension Remove')
