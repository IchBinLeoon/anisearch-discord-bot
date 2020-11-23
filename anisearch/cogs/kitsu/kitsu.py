import datetime
from typing import Optional

import discord
from discord.ext import commands, menus

from anisearch.utils.database.profile import select_kitsu_profile
from anisearch.utils.formats import description_parser
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.requests import kitsu_request


class Kitsu(commands.Cog, name='Kitsu'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_profile_kitsu(self, ctx, username):
        embeds = []
        try:
            data = await kitsu_request('user', username)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the Kitsu Profile'
                                                             ' `{}`.'.format(username),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data['data'] is not None and len(data['data']) > 0:
            user = data['data'][0]
            try:
                if user['attributes']['createdAt']:
                    createdAt = user['attributes']['createdAt'].split('T')
                    createdAt = createdAt[0]
                else:
                    createdAt = '-'
                if user['attributes']['updatedAt']:
                    updatedAt = user['attributes']['updatedAt'].split('T')
                    updatedAt = updatedAt[0]
                else:
                    updatedAt = '-'
                if user['attributes']['location']:
                    location = user['attributes']['location']
                else:
                    location = '-'
                if user['attributes']['birthday']:
                    birthday = user['attributes']['birthday']
                else:
                    birthday = '-'
                if user['attributes']['gender']:
                    gender = user['attributes']['gender'].replace('male', 'Male').replace('feMale', 'Female')
                else:
                    gender = '-'
                embed = discord.Embed(title=user['attributes']['name'], description=f'**Gender:** {gender}\n'
                                                                                    f'**Birthday:** {birthday}\n'
                                                                                    f'**Location:** {location}\n'
                                                                                    f'**Created at:** {createdAt}\n'
                                                                                    f'**Updated at:** {updatedAt}\n',
                                      timestamp=ctx.message.created_at, color=0x4169E1)
                if user['id']:
                    embed.url = 'https://kitsu.io/users/{}'.format(user['id'])
                if user['attributes']['avatar']:
                    embed.set_thumbnail(url=user['attributes']['avatar']['original'])
                if user['attributes']['coverImage']:
                    embed.set_image(url=user['attributes']['coverImage']['original'])
                if user['attributes']['about']:
                    about = user['attributes']['about'][0:1000] + '...'
                    embed.add_field(name='About', value=about, inline=False)
                try:
                    anime_stats = data['included'][22]
                    manga_stats = data['included'][20]
                    anime_days_watched = str(datetime.timedelta(seconds=anime_stats['attributes']['statsData']
                                                                ['time'])).split(',')
                    anime_days_watched = anime_days_watched[0]
                    anime_completed = anime_stats['attributes']['statsData']['completed']
                    anime_episodes_watched = anime_stats['attributes']['statsData']['units']
                    anime_total_entries = anime_stats['attributes']['statsData']['media']
                    manga_total_entries = manga_stats['attributes']['statsData']['media']
                    manga_chapters = manga_stats['attributes']['statsData']['units']
                    manga_completed = manga_stats['attributes']['statsData']['completed']
                    embed.add_field(name='Anime Stats', value=f'Days Watched: {anime_days_watched}\n'
                                                              f'Completed: {anime_completed}\n'
                                                              f'Episodes: {anime_episodes_watched}\n'
                                                              f'Total Entries: {anime_total_entries}\n',
                                    inline=True)
                    embed.add_field(name='Manga Stats', value=f'Completed: {manga_completed}\n'
                                                              f'Chapters Read: {manga_chapters}\n'
                                                              f'Total Entries: {manga_total_entries}\n',
                                    inline=True)
                except Exception as exception:
                    logger.exception(exception)
                    pass
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                 'the Kitsu Profile.',
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
        return embeds

    @commands.command(name='kitsu', aliases=['k', 'kit'], usage='kitsu <username|@member>', brief='5s',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_kitsu(self, ctx, username: Optional[str]):
        """Displays information about the given Kitsu Profile such as anime stats and manga stats!"""
        async with ctx.channel.typing():
            if username is None:
                user_id = ctx.author.id
                try:
                    username = select_kitsu_profile(user_id)
                except Exception as exception:
                    logger.exception(exception)
                    username = None
            elif username.startswith('<@!'):
                user_id = int(username.replace('<@!', '').replace('>', ''))
                try:
                    username = select_kitsu_profile(user_id)
                except Exception as exception:
                    logger.exception(exception)
                    username = None
            else:
                username = username
            if username:
                embeds = await self._search_profile_kitsu(ctx, username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title='The Kitsu Profile `{}` could not be found.'.format(username),
                                          color=0xff0000)
                    await ctx.channel.send(embed=embed)
            else:
                error_embed = discord.Embed(title='No Kitsu Profile set.', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
