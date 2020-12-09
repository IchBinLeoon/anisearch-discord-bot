from anisearch.cogs.settings.settings import Settings
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Settings(bot))
    logger.info('Loaded cog Settings')
