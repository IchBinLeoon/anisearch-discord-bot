from anisearch.cogs.events.events import Events
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Events(bot))
    logger.info('Loaded cog Events')
