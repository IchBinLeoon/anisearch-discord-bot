from anisearch.bot import logger
from anisearch.cogs.studio.studio import Studio


def setup(bot):
    bot.add_cog(Studio(bot))
    logger.info('Loaded extension Studio')


def teardown():
    logger.info('Unloaded extension Studio')
