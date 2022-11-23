import logging

from discord.ext import commands

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


class Notification(commands.Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Notification(bot))
