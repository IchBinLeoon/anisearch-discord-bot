from anisearch.bot import logger
from anisearch.cogs.contact.contact import Contact


def setup(bot):
    bot.add_cog(Contact(bot))
    logger.info('Loaded extension Contact')


def teardown():
    logger.info('Unloaded extension Contact')
