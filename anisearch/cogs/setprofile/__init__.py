from anisearch.bot import logger
from anisearch.cogs.setprofile.setprofile import SetProfile


def setup(bot):
    bot.add_cog(SetProfile(bot))
    logger.info('Loaded extension SetProfile')


def teardown():
    logger.info('Unloaded extension SetProfile')
