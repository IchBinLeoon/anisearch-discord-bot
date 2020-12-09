from anisearch.cogs.image.image import Image
from anisearch.utils.logger import logger


def setup(bot):
    bot.add_cog(Image(bot))
    logger.info('Loaded cog Image')
