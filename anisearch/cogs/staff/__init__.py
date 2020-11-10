from anisearch.bot import logger
from anisearch.cogs.staff.staff import Staff


def setup(bot):
    bot.add_cog(Staff(bot))
    logger.info('Loaded extension Staff')


def teardown():
    logger.info('Unloaded extension Staff')
