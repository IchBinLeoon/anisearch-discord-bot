from animesearch.cogs.character.character import Character
from animesearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Character(bot))
    logger.info('Loaded cog Character')


def teardown():
    logger.info('Unloaded cog Character')
