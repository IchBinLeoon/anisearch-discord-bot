from animesearch.cogs.staff.staff import Staff
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Staff(bot))
    logger.info('Loaded cog Staff')


def teardown():
    logger.info('Unloaded cog Staff')
