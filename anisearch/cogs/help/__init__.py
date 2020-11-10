from anisearch.bot import logger
from anisearch.cogs.help.help import Help


def setup(bot):
    bot.add_cog(Help(bot))
    logger.info('Loaded extension Help')


def teardown():
    logger.info('Unloaded extension Help')
