import logging

import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX

log = logging.getLogger(__name__)


class Settings(commands.Cog, name='Settings'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @commands.command(name='setprefix', usage='setprefix <prefix>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setprefix(self, ctx: Context, prefix: str):
        """Changes the server prefix. Can only be used by a server administrator."""
        if len(prefix) > 5:
            embed = nextcord.Embed(
                title='The prefix cannot be longer than 5 characters.', color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        else:
            prefix_old = self.bot.db.get_prefix(ctx.message)
            self.bot.db.update_prefix(ctx.message, prefix)
            prefix_new = self.bot.db.get_prefix(ctx.message)
            if prefix_new == DEFAULT_PREFIX:
                embed = nextcord.Embed(
                    title=f'{ctx.author} reset the prefix.', color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                embed = nextcord.Embed(
                    title=f'{ctx.author} changed the prefix from `{prefix_old}` to `{prefix_new}`.',
                    color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)


def setup(bot: AniSearchBot):
    bot.add_cog(Settings(bot))
    log.info('Settings cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Settings cog unloaded')
