from animesearch.cogs.studio.studio import Studio
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Studio(bot))
    logger.info('Loaded cog Studio')


def teardown():
    logger.info('Unloaded cog Studio')
