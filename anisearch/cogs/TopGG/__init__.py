from anisearch.cogs.TopGG.TopGG import TopGG
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(TopGG(bot))
    logger.info('Loaded cog TopGG')


def teardown():
    logger.info('Unloaded cog TopGG')
