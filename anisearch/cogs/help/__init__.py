from anisearch.cogs.help.help import Help
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Help(bot))
    logger.info('Loaded cog Help')
