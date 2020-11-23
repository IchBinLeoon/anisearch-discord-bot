from anisearch.cogs.staff.staff import Staff
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Staff(bot))
    logger.info('Loaded cog Staff')


def teardown():
    logger.info('Unloaded cog Staff')
