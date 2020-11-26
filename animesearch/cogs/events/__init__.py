from animesearch.cogs.events.events import Events
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Events(bot))
    logger.info('Loaded cog Events')


def teardown():
    logger.info('Unloaded cog Events')
