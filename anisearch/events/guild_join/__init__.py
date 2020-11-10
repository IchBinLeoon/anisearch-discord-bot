from anisearch.events.guild_join.guild_join import GuildJoin
from anisearch.bot import logger


def setup(bot):
    bot.add_cog(GuildJoin(bot))
    logger.info('Loaded extension GuildJoin')


def teardown():
    logger.info('Unloaded extension GuildJoin')
