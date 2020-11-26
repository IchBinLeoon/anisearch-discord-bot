from animesearch.cogs.help.help import Help
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Help(bot))
    logger.info('Loaded cog Help')


def teardown():
    logger.info('Unloaded cog Help')
