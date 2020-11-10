from anisearch.cogs.character.character import Character
from anisearch.bot import logger


def setup(bot):
    bot.add_cog(Character(bot))
    logger.info('Loaded extension Character')


def teardown():
    logger.info('Unloaded extension Character')
