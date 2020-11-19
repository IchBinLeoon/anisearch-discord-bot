import discord
from discord.ext import commands, menus
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.requests import kitsu_request_user


class Kitsu(commands.Cog, name='Kitsu'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_profile_kitsu(self, ctx, username):
        embeds = []
        try:
            data = await kitsu_request_user(username)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the Kitsu Profile'
                                                             ' `{}`.\n\n **Exception:** `{}`'.format(username,
                                                                                                     exception),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data['data'] is not None and len(data['data']) > 0:
            user = data['data'][0]
            try:
                embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                if user['attributes']['name']:
                    embed.title = user['attributes']['name']
                if user['id']:
                    embed.url = 'https://kitsu.io/users/{}'.format(user['id'])
                if user['attributes']['avatar']['original']:
                    embed.set_thumbnail(url=user['attributes']['avatar']['original'])

                print(user)

                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                 'the Kitsu Profile.\n\n**Exception:** `{}`'
                                      .format(exception),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
        return embeds

    @commands.command(name='kitsu', aliases=['k', 'kit'], usage='kitsu <username>', brief='5s',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_kitsu(self, ctx, *, username):
        """Displays information about the given Kitsu Profile."""
        async with ctx.channel.typing():
            embeds = await self._search_profile_kitsu(ctx, username)
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title='The Kitsu Profile `{}` could not be found.'.format(username),
                                      color=0xff0000)
                await ctx.channel.send(embed=embed)
