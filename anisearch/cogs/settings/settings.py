"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

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
    @commands.guild_only()
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
