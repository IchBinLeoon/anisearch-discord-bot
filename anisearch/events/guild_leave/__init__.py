from anisearch.bot import logger
from anisearch.events.guild_leave.guild_leave import GuildLeave


def setup(bot):
    bot.add_cog(GuildLeave(bot))
    logger.info('Loaded extension GuildLeave')


def teardown():
    logger.info('Unloaded extension GuildLeave')
