from anisearch.cogs.admin.admin import Admin
from anisearch.bot import logger


def setup(bot):
    bot.add_cog(Admin(bot))
    logger.info('Loaded extension Admin')


def teardown():
    logger.info('Unloaded extension Admin')
