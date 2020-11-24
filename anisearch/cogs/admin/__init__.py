from anisearch.cogs.admin.admin import Admin
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Admin(bot))
    logger.info('Loaded cog Admin')


def teardown():
    logger.info('Unloaded cog Admin')