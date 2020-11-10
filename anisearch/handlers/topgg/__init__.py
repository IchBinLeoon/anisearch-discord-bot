from anisearch.bot import logger
from anisearch.handlers.topgg.topgg import TopGG


def setup(bot):
    bot.add_cog(TopGG(bot))
    logger.info('Loaded extension TopGG')


def teardown():
    logger.info('Unloaded extension TopGG')
