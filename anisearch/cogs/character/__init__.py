from anisearch.cogs.character.character import Character
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Character(bot))
    logger.info('Loaded cog Character')
