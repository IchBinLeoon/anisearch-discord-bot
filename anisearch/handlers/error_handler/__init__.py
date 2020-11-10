from anisearch.bot import logger
from anisearch.handlers.error_handler.error_handler import ErrorHandler


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
    logger.info('Loaded extension ErrorHandler')


def teardown():
    logger.info('Unloaded extension ErrorHandler')
