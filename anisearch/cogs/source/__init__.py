from anisearch.bot import logger
from anisearch.cogs.source.source import Source


def setup(bot):
    bot.add_cog(Source(bot))
    logger.info('Loaded extension Source')


def teardown():
    logger.info('Unloaded extension Source')
