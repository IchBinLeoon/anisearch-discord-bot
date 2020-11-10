from anisearch.cogs.about.about import About
from anisearch.bot import logger


def setup(bot):
    bot.add_cog(About(bot))
    logger.info('Loaded extension About')


def teardown():
    logger.info('Unloaded extension About')
