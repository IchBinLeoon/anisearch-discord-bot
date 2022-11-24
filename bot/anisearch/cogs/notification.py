import logging

from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


class Notification(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Notification(bot))
