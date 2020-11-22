import discord
from discord.ext import commands
from anisearch.utils.database.prefix import change_prefix
from anisearch.utils.database.prefix import select_prefix


class Settings(commands.Cog, name='Settings'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='prefix', usage='prefix <prefix>', brief='10s', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def cmd_prefix(self, ctx, prefix):
        """Changes the current server prefix."""
        if len(prefix) > 5:
            error_embed = discord.Embed(title='The prefix cannot be longer than 5 characters.',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
        else:
            prefix_old = select_prefix(ctx)
            prefix_new = change_prefix(ctx, prefix)
            if prefix_new == 'as!':
                embed = discord.Embed(title='Prefix resetted.', color=0x4169E1)
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='{} changed the prefix from `{}` to `{}`.'.format(ctx.author,
                                                                                              prefix_old, prefix_new),
                                      color=0x4169E1)
                await ctx.channel.send(embed=embed)
